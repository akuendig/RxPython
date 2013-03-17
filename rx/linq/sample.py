from rx.disposable import CompositeDisposable, SingleAssignmentDisposable
from rx.observable import Producer
from rx.observer import Observer
from .sink import Sink
from threading import RLock


class SampleWithObservable(Producer):
  def __init__(self, source, sampler):
    self.source = source
    self.sampler = sampler

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(SampleWithObservable.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.gate = RLock()
      self.atEnd = False
      self.hasValue = False
      self.value = None
      self.sourceSubscription = SingleAssignmentDisposable()
      self.sourceSubscription.disposable = self.parent.source.subscribeSafe(self)

      samplerSubscription = self.parent.sampler.subscribeSafe(self.SamplerObserver(self))

      return CompositeDisposable(self.sourceSubscription, samplerSubscription)

    def onNext(self, value):
      with self.gate:
        self.hasValue = True
        self.value = value

    def onError(self, exception):
      with self.gate:
        self.observer.onError(exception)
        self.dispose()

    def onCompleted(self):
      with self.gate:
        self.atEnd = True
        self.sourceSubscription.dispose()

    class SamplerObserver(Observer):
      def __init__(self, parent):
        self.parent = parent

      def onNext(self, value):
        with self.parent.gate:
          if self.parent.hasValue:
            self.parent.hasValue = False
            self.parent.observer.onNext(self.parent.value)

          if self.parent.atEnd:
            self.parent.observer.onCompleted()
            self.parent.dispose()

      def onError(self, exception):
        with self.parent.gate:
          self.parent.observer.onError(exception)
          self.parent.dispose()

      def onCompleted(self):
        with self.parent.gate:
          if self.parent.hasValue:
            self.parent.hasValue = False
            self.parent.observer.onNext(self.parent.value)

          if self.parent.atEnd:
            self.parent.observer.onCompleted()
            self.parent.dispose()


class SampleWithTime(Producer):
  def __init__(self, source, interval, scheduler):
    self.source = source
    self.interval = interval
    self.scheduler = scheduler

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(SampleWithTime.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.gate = RLock()
      self.atEnd = False
      self.hasValue = False
      self.value = None
      self.sourceSubscription = SingleAssignmentDisposable()
      self.sourceSubscription.disposable = self.parent.source.subscribeSafe(self)

      return CompositeDisposable(
        self.sourceSubscription,
        self.parent.scheduler.schedulePeriodic(self.parent.interval, self.tick)
      )

    def tick(self):
      with self.gate:
        if self.hasValue:
          self.hasValue = False
          self.observer.onNext(self.value)

        if self.atEnd:
          self.observer.onCompleted()
          self.dispose()

    def onNext(self, value):
      with self.gate:
        self.hasValue = True
        self.value = value

    def onError(self, exception):
      with self.gate:
        self.observer.onError(exception)
        self.dispose()

    def onCompleted(self):
      with self.gate:
        self.atEnd = True
        self.sourceSubscription.dispose()
