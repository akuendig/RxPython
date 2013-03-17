from rx.observable import Producer
from .sink import Sink


class DefaultIfEmpty(Producer):
  def __init__(self, source, defaultValue):
    self.source = source
    self.defaultValue = defaultValue

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  def getSources(self):
    return self.sources

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(DefaultIfEmpty.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.found = False

    def onNext(self, value):
      self.found = True
      self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      if not self.found:
        self.observer.onNext(self.parent.defaultValue)

      self.observer.onCompleted()
      self.dispose()