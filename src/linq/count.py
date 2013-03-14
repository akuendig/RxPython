from observable import Producer
from .sink import Sink


class Count(Producer):
  def __init__(self, source, predicate):
    self.source = source
    self.predicate = predicate

  def run(self, observer, cancel, setSink):
    sink = self.Sink(observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  def getSources(self):
    return self.sources

  class Sink(Sink):
    def __init__(self, observer, cancel):
      super(Count.Sink, self).__init__(observer, cancel)
      self.count = 0

    def onNext(self, value):
      try:
        if self.parent.predicate(value):
          self.count += 1
      except Exception as e:
        self.observer.onError(e)
        self.dispose()

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onNext(self.count)
      self.observer.onCompleted()
      self.dispose()