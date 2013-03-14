from disposable import CompositeDisposable, Disposable, SerialDisposable, SingleAssignmentDisposable
from observable import Producer
from observer import Observer
from internal import Struct
from scheduler import Scheduler
from .sink import Sink
from threading import Event, RLock, Semaphore


class DelayTime(Producer):
  def __init__(self, source, dueTime, scheduler, isAbsolute):
    self.source = source
    self.dueTime = dueTime
    self.scheduler = scheduler
    self.isAbsolute = isAbsolute

  def run(self, observer, cancel, setSink):
    if self.scheduler.isLongRunning:
      sink = self.LongrunningSink(self, observer, cancel)
      setSink(sink)
      return sink.run()
    else:
      sink = self.Sink(self, observer, cancel)
      setSink(sink)
      return sink.run()

  def eval(self):
    return self.observableFactory()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(DelayTime.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.scheduler = self.parent.scheduler

      self.cancel = SerialDisposable()

      self.gate = RLock()
      self.active = False # as soon as a value arrived
      self.running = False # on relative: True, on absolute: True after absolute time
      self.queue = []
      self.hasCompleted = False
      self.completeAt = 0
      self.hasFailed = False
      self.exception = None

      self.startTime = self.scheduler.now()

      if self.parent.isAbsolute:
        self.ready = False
        self.cancel.disposable = self.scheduler.scheduleWithAbsolute(
          self.parent.dueTime,
          self.start
        )
      else:
        self.ready = True
        self.delay = Scheduler.normalize(self.parent.dueTime)

      self.sourceSubscription = SingleAssignmentDisposable()
      self.sourceSubscription.disposable = self.parent.source.subscribeSafe(self)

      return CompositeDisposable(self.sourceSubscription, self.cancel)

    def elapsed(self):
      return self.scheduler.now() - self.startTime

    def start(self):
      next = 0
      shouldRun = False

      with self.gate:
        self.delay = self.elapsed()

        if len(self.queue) > 0:
          next = self.queue[0].interval

          for item in self.queue:
            item.interval += self.delay

          shouldRun = True
          self.active = True

        self.ready = True

      if shouldRun:
        self.cancel.disposable = self.scheduler.scheduleRecursiveWithRelative(
          next,
          self.drainQueue
        )

    def onNext(self, value):
      next = self.elapsed() + self.delay
      shouldRun = False

      with self.gate:
        self.queue.append(Struct(value=value, interval=next))
        shouldRun = self.ready and (not self.active)
        self.active = True

      if shouldRun:
        self.cancel.disposable = self.scheduler.scheduleRecursiveWithRelative(
          self.delay,
          self.drainQueue
        )

    def onError(self, exception):
      self.sourceSubscription.dispose()

      shouldRun = False

      with self.gate:
        self.queue.clear()

        self.exception = exception
        self.hasFailed = True

        shouldRun = not self.running

      if shouldRun:
        self.observer.onError(exception)
        self.dispose()

    def onCompleted(self):
      self.sourceSubscription.dispose()

      next = self.elapsed() + self.delay
      shouldRun = False

      with self.gate:
        self.completeAt = next
        self.hasCompleted = True

        shouldRun = self.ready and (not self.active)
        self.active = True

      if shouldRun:
        self.cancel.disposable = self.scheduler.scheduleRecursiveWithRelative(
          self.delay,
          self.drainQueue
        )

    def drainQueue(self, recurse):
      with self.gate:
        if self.hasFailed:
          return
        self.running = True


      #
      # The shouldYield flag was added to address TFS 487881: "Delay can be unfair". In the old
      # implementation, the loop below kept running while there was work for immediate dispatch,
      # potentially causing a long running work item on the target scheduler. With the addition
      # of long-running scheduling in Rx v2.0, we can check whether the scheduler supports this
      # interface and perform different processing (see λ). To reduce the code churn in the old
      # loop code here, we set the shouldYield flag to true after the first dispatch iteration,
      # in order to break from the loop and enter the recursive scheduling path.

      shouldYield = False

      while True:
        hasFailed = False
        error = NotImplementedError

        hasValue = False
        value = NotImplementedError
        hasCompleted = False

        shouldRecurse = False
        recurseDueTime = 0

        with self.gate:
          if self.hasFailed:
            error = self.exception
            hasFailed = True
            self.running = False
          else:
            now = self.elapsed()

            if len(self.queue) > 0:
              nextDue = self.queue[0].interval

              if nextDue <= now and not shouldYield:
                value = self.queue[0].value
                hasValue = True
                self.queue = self.queue[1:]
              else:
                shouldRecurse = True
                recurseDueTime = Scheduler.normalize(nextDue - now)
                self.running = False
            elif self.hasCompleted:
              if self.completeAt < now and not shouldYield:
                hasCompleted = True
              else:
                shouldRecurse = True
                recurseDueTime = Scheduler.normalize(nextDue - now)
                self.running = False
            else:
              self.running = False
              self.active = False
        # end with self.gate

        if hasValue:
          self.observer.onNext(value)
          shouldYield = True
        else:
          if hasCompleted:
            self.observer.onCompleted()
            self.dispose()
          elif hasFailed:
            self.observer.onError(error)
            self.dispose()
          elif shouldRecurse:
            recurse(recurseDueTime)

          return
      #end while
    # end Sink

  class LongrunningSink(Sink):
    def __init__(self, parent, observer, cancel):
      super(DelayTime.LongrunningSink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.scheduler = self.parent.scheduler

      self.cancel = SerialDisposable()

      self.gate = RLock()
      self.evt = Semaphore(0)
      self.stopped = False
      self.stop = Event()
      self.queue = []
      self.hasCompleted = False
      self.completeAt = 0
      self.hasFailed = False
      self.exception = None

      self.startTime = self.scheduler.now()

      if self.parent.isAbsolute:
        self.cancel.disposable = self.scheduler.scheduleAbsolute(
          self.parent.dueTime,
          self.start
        )
      else:
        self.delay = Scheduler.normalize(self.parent.dueTime)
        self.scheduleDrain()

      self.sourceSubscription = SingleAssignmentDisposable()
      self.sourceSubscription.disposable = self.parent.source.subscribeSafe(self)

      return CompositeDisposable(self.sourceSubscription, self.cancel)

    def elapsed(self):
      return self.scheduler.now() - self.startTime

    def start(self):
      with self.gate:
        self.delay = self.elapsed()

        for item in self.queue:
          item.interval += self.delay

      self.scheduleDrain()

    def scheduleDrain(self):
      def cancel():
        self.stopped = True
        self.stop.set()
        self.evt.release()

      self.stop.clear()
      self.cancel.disposable = Disposable.create(cancel)
      self.scheduler.scheduleLongRunning(self.drainQueue)

    def onNext(self, value):
      next = self.elapsed() + self.delay

      with self.gate:
        self.queue.append(Struct(value=value, interval=next))
        self.evt.release()

    def onError(self, exception):
      self.sourceSubscription.dispose()

      with self.gate:
        self.queue.clear()

        self.exception = exception
        self.hasFailed = True

        self.evt.release()

    def onCompleted(self):
      self.sourceSubscription.dispose()

      next = self.elapsed() + self.delay

      with self.gate:
        self.completeAt = next
        self.hasCompleted = True

        self.evt.release()

    def drainQueue(self, cancel):
      while True:
        self.evt.acquire()
        if self.stopped:
          return

        hasFailed = False
        error = NotImplementedError

        hasValue = False
        value = NotImplementedError
        hasCompleted = False

        shouldWait = False
        waitTime = 0

        with self.gate:
          if self.hasFailed:
            error = self.exception
            hasFailed = True
          else:
            now = self.elapsed()

            if len(self.queue) > 0:
              next = self.queue[0]

              hasValue = True
              value = next.value

              nextDue = next.interval
              if nextDue > now:
                shouldWait = True
                waitTime = Scheduler.normalize(nextDue - now)
            elif self.hasCompleted:
              hasCompleted = True

              if self.completeAt > now:
                shouldWait = True
                waitTime = Scheduler.normalize(self.completeAt - now)
        # end with self.gate

        if shouldWait:
          timer = Event()
          self.scheduler.scheduleWithRelative(waitTime, lambda: timer.set())
          timer.wait()

        if hasValue:
          self.observer.onNext(value)
        else:
          if hasCompleted:
            self.observer.onCompleted()
            self.dispose()
          elif hasFailed:
            self.observer.onError(error)
            self.dispose()

          return
      #end while
    # end Sink


class DelayObservable(Producer):
  def __init__(self, source, subscriptionDelay, delaySelector):
    self.source = source
    self.subscriptionDelay = subscriptionDelay
    self.delaySelector = delaySelector

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(DelayObservable.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.delays = CompositeDisposable()
      self.gate = RLock()
      self.atEnd = False
      self.subscription = SerialDisposable()

      if self.parent.subscriptionDelay == None:
        self.start()
      else:
        self.subscription.disposable = self.parent.subscriptionDelay.subscribeSafe(self.Sigma(self))

      return CompositeDisposable(self.subscription, self.delays)

    def start(self):
      self.subscription.disposable = self.parent.source.subscribeSafe(self)

    def onNext(self, value):
      try:
        delay = self.parent.delaySelector(value)
      except Exception as e:
        with self.gate:
          self.observer.onError(e)
          self.dispose()
      else:
        d = SingleAssignmentDisposable()
        self.delays.add(d)
        d.disposable = delay.subscribeSafe(self.Delta(self, value, d))

    def onError(self, exception):
      with self.gate:
        self.observer.onError(exception)
        self.dispose()

    def onCompleted(self):
      with self.gate:
        self.atEnd = True
        self.subscription.dispose()

        self.checkDone()

    def checkDone(self):
      if self.atEnd and self.delays.length == 0:
        self.observer.onCompleted()
        self.dispose()

    class Sigma(Observer):
      def __init__(self, parent):
        self.parent = parent

      def onNext(self, value):
        self.parent.start()

      def onError(self, exception):
        self.parent.observer.onError(exception)
        self.parent.dispose()

      def onCompleted(self):
        self.parent.start()

    class Delta(Observer):
      def __init__(self, parent, value, cancelSelf):
        self.parent = parent
        self.value = value
        self.cancelSelf = cancelSelf

      def onNext(self, delay):
        with self.parent.gate:
          self.parent.observer.onNext(self.value)
          self.parent.delays.remove(self.cancelSelf)
          self.parent.checkDone()

      def onError(self, exception):
        with self.parent.gate:
          self.parent.observer.onError(exception)
          self.parent.dispose()

      def onCompleted(self):
        with self.parent.gate:
          self.parent.observer.onNext(self.value)
          self.parent.delays.remove(self.cancelSelf)
          self.parent.checkDone()


class DelaySubscription(Producer):
  def __init__(self, source, dueTime, scheduler, isAbsolute):
    self.source = source
    self.dueTime = dueTime
    self.scheduler = scheduler
    self.isAbsolute = isAbsolute

  def run(self, observer, cancel, setSink):
    sink = self.Sink(observer, cancel)
    setSink(sink)

    if self.isAbsolute:
      return self.scheduler.scheduleWithAbsoluteAndState(
        sink,
        self.dueTime,
        self.delaySubscribe
      )
    else:
      return self.scheduler.scheduleWithRelativeAndState(
        sink,
        self.dueTime,
        self.delaySubscribe
      )

  def delaySubscribe(self, scheduler, sink):
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, observer, cancel):
      super(DelaySubscription.Sink, self).__init__(observer, cancel)

    def onNext(self, value):
      self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()
