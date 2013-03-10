from observable import Producer
from .sink import Sink


class IgnoreElements(Producer):
  def __init__(self, source):
    self.source = source

  def run(self, observer, cancel, setSink):
    sink = self.Sink(observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, observer, cancel):
      super(IgnoreElements.Sink, self).__init__(observer, cancel)

    def onNext(self, value):
      pass

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()