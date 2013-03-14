from observable import Producer
from .sink import Sink


class Any(Producer):
  def __init__(self, source, predicate):
    self.source = source
    self.predicate = predicate

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(Any.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def onNext(self, value):
      res = False

      try:
        res = self.parent.predicate(value)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
        return

      if res:
        self.observer.onNext(True)
        self.observer.onCompleted()
        self.dispose()

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onNext(False)
      self.observer.onCompleted()
      self.dispose()