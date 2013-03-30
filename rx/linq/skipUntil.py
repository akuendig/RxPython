from rx.concurrency import Atomic
from rx.disposable import CompositeDisposable, SingleAssignmentDisposable
from rx.observable import Producer
from rx.observer import Observer, NoopObserver
import rx.linq.sink


class SkipUntilObservable(Producer):
  def __init__(self, source, other):
    self.source = source
    self.other = other

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(SkipUntilObservable.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      sourceObserver = self.T(self)
      otherObserver = self.O(self, sourceObserver)

      sourceSubscription = self.parent.source.subscribeSafe(sourceObserver)
      otherSubscription = self.parent.other.subscribeSafe(otherObserver)

      sourceObserver.disposable = sourceSubscription
      otherObserver.disposable = otherSubscription

      return CompositeDisposable(sourceSubscription, otherSubscription)

    class T(Observer):
      def __init__(self, parent):
        self.parent = parent
        self.observer = NoopObserver()
        self.subscription = SingleAssignmentDisposable()

      def setdisposable(self, value):
        self.subscription.disposable = value
      disposable = property(None, setdisposable)

      def onNext(self, value):
        self.observer.onNext(value)

      def onError(self, exception):
        self.parent.observer.onError(exception)
        self.parent.dispose()

      def onCompleted(self):
        self.observer.onCompleted()
        # We can't cancel the other stream yet, it may be on its way
        # to dispatch an OnError message and we don't want to have a race.
        self.subscription.dispose()

    class O(Observer):
      def __init__(self, parent, sourceObserver):
        self.parent = parent
        self.sourceObserver = sourceObserver
        self.subscription = SingleAssignmentDisposable()

      def setdisposable(self, value):
        self.subscription.disposable = value
      disposable = property(None, setdisposable)

      def onNext(self, value):
        self.sourceObserver.observer = self.parent.observer
        self.subscription.dispose()

      def onError(self, exception):
        self.parent.observer.onError(exception)
        self.parent.dispose()

      def onCompleted(self):
        self.subscription.dispose()


class SkipUntilTime(Producer):
  def __init__(self, source, startTime, scheduler):
    self.source = source
    self.startTime = startTime
    self.scheduler = scheduler

  def omega(self, startTime):
    if startTime <= self.startTime:
      return self
    else:
      return SkipUntilTime(self.source, startTime, self.scheduler)

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(SkipUntilTime.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.open = Atomic(False)

    def run(self):
      t = self.parent.scheduler.scheduleWithAbsolute(self.parent.startTime, self.tick)
      d = self.parent.source.subscribeSafe(self)

      return CompositeDisposable(t, d)

    def tick(self):
      self.open.value = True

    def onNext(self, value):
      if self.open.value:
        self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()