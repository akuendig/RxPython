from observable import Producer
from .sink import Sink


class DistinctUntilChanged(Producer):
  def __init__(self, source, predicate=lambda _: True, throwOnEmpty):
    self.source = source
    self.predicate = predicate
    self.throwOnEmpty = throwOnEmpty

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(DistinctUntilChanged.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.currentKey = None
      self.hasCurrentKey = False

    def onNext(self, value):
      try:
        b = self.parent.predicate(value)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
      else:
        self.observer.onNext(value)
        self.observer.onCompleted()
        self.dispose()

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      if self.parent.throwOnEmpty:
        self.observer.onError(Exception("Invalid operation"))
      else:
        self.observer.onNext(None)
        self.observer.onCompleted()

      self.dispose()