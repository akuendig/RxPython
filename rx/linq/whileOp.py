from rx.observable import Producer
from .sink import ConcatSink


class While(Producer):
  def __init__(self, condition, source):
    self.condition = condition
    self.source = source

  def run(self, observer, cancel, setSink):
    sink = self.Sink(observer, cancel)
    setSink(sink)
    return sink.run(self.getSources())

  def getSources(self):
    while self.condition():
      yield self.source

  class Sink(ConcatSink):
    def __init__(self, observer, cancel):
      super(While.Sink, self).__init__(observer, cancel)

    def onNext(self, value):
      self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()