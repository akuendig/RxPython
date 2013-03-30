from rx.disposable import CompositeDisposable, Disposable, SerialDisposable, SingleAssignmentDisposable
from rx.observable import Producer
from rx.observer import Observer
import rx.linq.sink
from threading import RLock


class ThrottleTime(Producer):
  def __init__(self, source, dueTime, scheduler):
    self.source = source
    self.dueTime = dueTime
    self.scheduler = scheduler

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(ThrottleTime.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.gate = RLock()
      self.value = None
      self.hasValue = False
      self.propagatorDisposable = SerialDisposable()
      self.resourceId = 0

      subscription = self.parent.source.subscribeSafe(self)

      return CompositeDisposable(subscription, self.propagatorDisposable)

    def onNext(self, value):
      currentId = 0

      with self.gate:
        self.hasValue = True
        self.value = value
        self.resourceId += 1
        currentId = self.resourceId

      d = SingleAssignmentDisposable()
      self.propagatorDisposable.disposable = d
      d.disposable = self.parent.scheduler.scheduleWithRelativeAndState(
        currentId,
        self.parent.dueTime,
        self.propagate
      )

    def propagate(self, scheduler, currentId):
      with self.gate:
        if self.hasValue and self.resourceId == currentId:
          self.observer.onNext(self.value)
        self.hasValue = False

      return Disposable.empty()

    def onError(self, exception):
      self.propagatorDisposable.dispose()

      with self.gate:
        self.observer.onError(exception)
        self.dispose()

        self.hasValue = False
        self.resourceId += 1

    def onCompleted(self):
      self.propagatorDisposable.dispose()

      with self.gate:
        if self.hasValue:
          self.observer.onNext(self.value)

        self.observer.onCompleted()
        self.dispose()

        self.hasValue = False
        self.resourceId += 1


class ThrottleObservable(Producer):
  def __init__(self, source, throttleSelector):
    self.source = source
    self.throttleSelector = throttleSelector

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(ThrottleObservable.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.gate = RLock()
      self.value = None
      self.hasValue = False
      self.throttleDisposable = SerialDisposable()
      self.resourceId = 0

      subscription = self.parent.source.subscribeSafe(self)

      return CompositeDisposable(subscription, self.throttleDisposable)

    def onNext(self, value):
      throttle = None

      try:
        throttle = self.parent.throttleSelector(value)
      except Exception as e:
        with self.gate:
          self.observer.onError(e)
          self.dispose()

        return

      currentId = 0

      with self.gate:
        self.hasValue = True
        self.value = value
        self.resourceId += 1
        currentId = self.resourceId

      d = SingleAssignmentDisposable()
      self.throttleDisposable.disposable = d
      d.disposable = throttle.subscribeSafe(self.Delta(self, value, currentId, d))

    def onError(self, exception):
      self.throttleDisposable.dispose()

      with self.gate:
        self.observer.onError(exception)
        self.dispose()

        self.hasValue = False
        self.resourceId += 1

    def onCompleted(self):
      self.throttleDisposable.dispose()

      with self.gate:
        if self.hasValue:
          self.observer.onNext(self.value)

        self.observer.onCompleted()
        self.dispose()

        self.hasValue = False
        self.resourceId += 1

    class Delta(Observer):
      def __init__(self, parent, value, currentId, cancelSelf):
        self.parent = parent
        self.value = value
        self.currentId = currentId
        self.cancelSelf = cancelSelf

      def onNext(self, value):
        with self.parent.gate:
          if self.parent.hasValue and self.parent.resourceId == self.currentId:
            self.parent.observer.onNext(self.value)

          self.parent.hasValue = False
          self.cancelSelf.dispose()

      def onError(self, exception):
        with self.parent.gate:
          self.parent.observer.onError(exception)
          self.parent.dispose()

      def onCompleted(self):
        with self.parent.gate:
          if self.parent.hasValue and self.parent.resourceId == self.currentId:
            self.parent.observer.onNext(self.value)

          self.parent.hasValue = False
          self.cancelSelf.dispose()
