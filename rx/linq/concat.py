from rx.observable import Producer
from .sink import ConcatSink


class Concat(Producer):
  def __init__(self, sources):
    self.sources = sources

  def run(self, observer, cancel, setSink):
    sink = self.Sink(observer, cancel)
    setSink(sink)
    return sink.run(self.sources)

  def getSources(self):
    return self.sources

  class Sink(ConcatSink):
    def __init__(self, observer, cancel):
      super(Concat.Sink, self).__init__(observer, cancel)

    def onNext(self, value):
      self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()