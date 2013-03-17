from rx.disposable import Disposable
from rx.observable import Producer
from .sink import Sink
from threading import RLock


class RefCount(Producer):
  def __init__(self, source):
    self.source = source
    self.gate = RLock()
    self.count = 0
    self.connectableSubscription = None

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(RefCount.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      subscription = self.parent.source.subscribeSafe(self)

      with self.parent.gate:
        self.parent.count += 1

        if self.parent.count == 1:
          self.parent.connectableSubscription = self.parent.source.connect()

      def dispose():
        subscription.dispose()

        with self.parent.gate:
          self.parent.count -= 1

          if self.parent.count == 0:
            self.parent.connectableSubscription.dispose()

      return Disposable.create(dispose)

    def onNext(self, value):
      self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()