from disposable import CompositeDisposable, SerialDisposable, SingleAssignmentDisposable
from observable import Producer
from observer import Observer
from .sink import Sink
from threading import RLock


class Switch(Producer):
  def __init__(self, sources):
    self.sources = sources

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(Switch.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.gate = RLock()
      self.innerSubscription = SerialDisposable()
      self.isStopped = False
      self.latest = 0
      self.hasLatest = False

      self.subscription = SingleAssignmentDisposable()
      self.subscription.disposable = self.parent.sources.subscribeSafe(self)

      return CompositeDisposable(self.subscription, self.innerSubscription)

    def onNext(self, value):
      observerId = 0

      with self.gate:
        self.latest += 1
        observerId = self.latest
        self.hasLatest = True

      d = SingleAssignmentDisposable()
      self.innerSubscription.disposable = d
      d.disposable = value.subscribeSafe(self.IdObserver(self, observerId, d))

    def onError(self, exception):
      with self.gate:
        self.observer.onError(exception)

      self.dispose()

    def onCompleted(self):
      with self.gate:
        self.subscription.dispose()
        self.isStopped = True

        if not self.hasLatest:
          self.observer.onCompleted()
          self.dispose()

    class IdObserver(Observer):
      def __init__(self, parent, observerId, cancelSelf):
        self.parent = parent
        self.observerId = observerId
        self.cancelSelf = cancelSelf

      def onNext(self, value):
        with self.parent.gate:
          if self.parent.latest == self.observerId:
            self.parent.observer.onNext(value)

      def onError(self, exception):
        with self.parent.gate:
          self.cancelSelf.dispose()

          if self.parent.latest == self.observerId:
            self.parent.observer.onError(exception)
            self.parent.dispose()

      def onCompleted(self):
        with self.parent.gate:
          self.cancelSelf.dispose()

          if self.parent.latest == self.observerId:
            self.parent.hasLatest = False

            if self.parent.isStopped:
              self.parent.observer.onCompleted()
              self.parent.dispose()
