from rx.observable import Producer
from .sink import ConcatSink


class DoWhile(Producer):
  def __init__(self, source, condition):
    self.source = source
    self.condition = condition

  def run(self, observer, cancel, setSink):
    sink = self.Sink(observer, cancel)
    setSink(sink)
    return sink.run(self.getSources())

  def getSources(self):
    yield self.source
    while self.condition():
      yield self.source

  class Sink(ConcatSink):
    def __init__(self, observer, cancel):
      super(DoWhile.Sink, self).__init__(observer, cancel)

    def onNext(self, value):
      self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()
