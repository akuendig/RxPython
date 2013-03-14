from observable import Producer
from .sink import Sink
from threading import RLock


class Synchronize(Producer):
  def __init__(self, source, gate):
    self.source = source
    self.gate = gate

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(Synchronize.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.gate = self.parent.gate

      if self.gate == None:
        self.gate = RLock()

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