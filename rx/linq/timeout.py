from disposable import CompositeDisposable, Disposable, SerialDisposable, SingleAssignmentDisposable
from observable import Producer
from observer import Observer
from .sink import Sink
from threading import RLock


class TimeoutAbsolute(Producer):
  def __init__(self, source, dueTime, other, scheduler):
    self.source = source
    self.dueTime = dueTime
    self.other = other
    self.scheduler = scheduler

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(TimeoutAbsolute.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.subscription = SerialDisposable()
      original = SingleAssignmentDisposable()

      self.subscription.disposable = original

      self.gate = RLock()
      self.switched = False

      timer = self.parent.scheduler.scheduleWithAbsolute(self.parent.dueTime, self.timeout)

      original.disposable = self.parent.soruce.subscribeSafe(self)

      return CompositeDisposable(self.subscription, timer)

    def timeout(self):
      timerWins = False

      with self.gate:
        timerWins = not self.switched
        self.switched = True

      if timerWins:
        self.subscription.disposable = self.parent.other.subscribeSafe(self.getForewarder())

    def onNext(self, value):
      with self.gate:
        if not self.switched:
          self.observer.onNext(value)

    def onError(self, exception):
      onErrorWins = False

      with self.gate:
        onErrorWins = not self.switched
        self.switched = True

      if onErrorWins:
        self.observer.onError(exception)
        self.dispose()

    def onCompleted(self):
      onCompletedWins = False

      with self.gate:
        onCompletedWins = not self.switched
        self.switched = True

      if onCompletedWins:
        self.observer.onCompleted()
        self.dispose()


class TimeoutRelative(Producer):
  def __init__(self, source, dueTime, other, scheduler):
    self.source = source
    self.dueTime = dueTime
    self.other = other
    self.scheduler = scheduler

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(TimeoutRelative.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.subscription = SerialDisposable()
      self.timer = SerialDisposable()
      original = SingleAssignmentDisposable()

      self.subscription.disposable = original

      self.gate = RLock()
      self.currentId = 0
      self.switched = False

      self.createTimer()

      original.disposable = self.parent.soruce.subscribeSafe(self)

      return CompositeDisposable(self.subscription, self.timer)

    def createTimer(self):
      self.timer = self.parent.scheduler.scheduleWithRelativeAndState(
        self.currentId,
        self.parent.dueTime,
        self.timeout
      )

    def timeout(self, scheduler, currentId):
      timerWins = False

      with self.gate:
        self.switched = self.currentId == currentId
        timerWins = self.switched

      if timerWins:
        self.subscription.disposable = self.parent.other.subscribeSafe(self.getForewarder())

      return Disposable.empty()

    def onNext(self, value):
      onNextWins = False

      with self.gate:
        onNextWins = not self.switched
        if onNextWins:
          self.currentId += 1

      if onNextWins:
        self.observer.onNext(value)
        self.createTimer()

    def onError(self, exception):
      onErrorWins = False

      with self.gate:
        onErrorWins = not self.switched
        if onErrorWins:
          self.currentId += 1

      if onErrorWins:
        self.observer.onError(exception)
        self.dispose()

    def onCompleted(self):
      onCompletedWins = False

      with self.gate:
        onCompletedWins = not self.switched
        if onCompletedWins:
          self.currentId += 1

      if onCompletedWins:
        self.observer.onCompleted()
        self.dispose()


class TimeoutObservable(Producer):
  def __init__(self, source, firstTimeout, timeoutSelector, other):
    self.source = source
    self.firstTimeout = firstTimeout
    self.timeoutSelector = timeoutSelector
    self.other = other

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(TimeoutObservable.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.subscription = SerialDisposable()
      self.timer = SerialDisposable()
      original = SingleAssignmentDisposable()

      self.subscription.disposable = original

      self.gate = RLock()
      self.currentId = 0
      self.switched = False

      self.setTimer(self.parent.firstTimeout)

      original.disposable = self.parent.soruce.subscribeSafe(self)

      return CompositeDisposable(self.subscription, self.timer)

    def onNext(self, value):
      if self.observerWins():
        self.observer.onNext(value)

        try:
          timeout = self.parent.timeoutSelector(value)
        except Exception as e:
          self.observer.onError(e)
          self.dispose()
        else:
          self.setTimer(timeout)

    def onError(self, exception):
      if self.observerWins():
        self.observer.onError(exception)
        self.dispose()

    def onCompleted(self):
      if self.observerWins():
        self.observer.onCompleted()
        self.dispose()

    def observerWins(self):
      res = False

      with self.gate:
        res = not self.switched
        if res:
          self.currentId += 1

      return res

    def setTimer(self, timeout):
      myId = self.currentId
      d = SingleAssignmentDisposable()
      self.timer.disposable = d
      d.disposable = timeout.subscribeSafe(self.Tau(self, myId, d))

    class Tau(Observer):
      def __init__(self, parent, currentId, cancelSelf):
        self.parent = parent
        self.currentId = currentId
        self.cancelSelf = cancelSelf

      def onNext(self, value):
        if self.timerWins():
          self.parent.subscription.disposable = self.parent.parent.other.subscribeSafe(self.parent.getForewarder())

        self.cancelSelf.dispose()

      def onError(self, exception):
        if self.timerWins():
          self.parent.observer.onError(exception)
          self.parent.dispose()

      def onCompleted(self):
        if self.timerWins():
          self.parent.subscription.disposable = self.parent.parent.other.subscribeSafe(self.parent.getForewarder())

      def timerWins(self):
        res = False

        with self.parent.gate:
          self.parent.switched = self.parent.currentId == self.currentId
          res = self.parent.switched

        return res
