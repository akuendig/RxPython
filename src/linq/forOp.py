from observable import Producer
from .sink import ConcatSink


class For(Producer):
  def __init__(self, source, resultSelector):
    self.source = source
    self.resultSelector = resultSelector

  def run(self, observer, cancel, setSink):
    sink = self.Sink(observer, cancel)
    setSink(sink)
    return sink.run(self.getSources())

  def getSources(self):
    for x in self.source:
      yield self.resultSelector(x)

  class Sink(ConcatSink):
    def __init__(self, observer, cancel):
      super(For.Sink, self).__init__(observer, cancel)

    def onNext(self, value):
      self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()