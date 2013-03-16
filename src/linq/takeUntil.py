from disposable import CompositeDisposable, SingleAssignmentDisposable
from observable import Producer
from observer import Observer
from .sink import Sink
from threading import RLock


class TakeUntilObservable(Producer):
  def __init__(self, source, other):
    self.source = source
    self.other = other

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(TakeUntilObservable.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.gate = RLock()

    def run(self):
      sourceObserver = self.T(self)
      otherObserver = self.O(self)

      sourceSubscription = self.parent.source.subscribeSafe(sourceObserver)
      otherSubscription = self.parent.other.subscribeSafe(otherObserver)

      sourceObserver.disposable = sourceSubscription
      otherObserver.disposable = otherSubscription

      return CompositeDisposable(sourceSubscription, otherSubscription)

    class T(Observer):
      def __init__(self, parent):
        self.parent = parent
        self.open = False

      def onNext(self, value):
        if self.open:
          self.observer.onNext(value)
        else:
          with self.parent.gate:
            self.parent.observer.onNext(value)

      def onError(self, exception):
        with self.parent.gate:
          self.parent.observer.onError(exception)
          self.parent.dispose()

      def onCompleted(self):
        with self.parent.gate:
          self.parent.observer.onCompleted()
          self.parent.dispose()

    class O(Observer):
      def __init__(self, parent, sourceObserver):
        self.parent = parent
        self.sourceObserver = sourceObserver
        self.subscription = SingleAssignmentDisposable()

      def setdisposable(self, value):
        self.subscription.disposable = value
      disposable = property(None, setdisposable)

      def onNext(self, value):
        with self.parent.gate:
          self.parent.observer.onCompleted()
          self.parent.dispose()

      def onError(self, exception):
        with self.parent.gate:
          self.parent.observer.onError(exception)
          self.parent.dispose()

      def onCompleted(self):
        with self.parent.gate:
          self.sourceObserver.open = True
          self.subscription.dispose()


class TakeUntilTime(Producer):
  def __init__(self, source, endTime, scheduler):
    self.source = source
    self.endTime = endTime
    self.scheduler = scheduler

  def omega(self, endTime):
    if endTime <= self.endTime:
      return self
    else:
      return TakeUntilTime(self.source, endTime, self.scheduler)

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(TakeUntilTime.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.gate = RLock()

      t = self.parent.scheduler.scheduleWithAbsolute(self.parent.endTime, self.tick)
      d = self.parent.source.subscribeSafe(self)

      return CompositeDisposable(t, d)

    def tick(self):
      with self.gate:
        self.observer.onCompleted()
        self.dispose()

    def onNext(self, value):
      with self.gate:
        self.observer.onNext(value)

    def onError(self, exception):
      with self.gate:
        self.observer.onError(exception)
        self.dispose()

    def onCompleted(self):
      with self.gate:
        self.observer.onCompleted()
        self.dispose()