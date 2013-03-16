from observable import Producer
from .sink import Sink


class OfType(Producer):
  def __init__(self, source, tpe):
    self.source = source
    self.tpe = tpe

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(OfType.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.currentKey = None
      self.hasCurrentKey = False

    def onNext(self, value):
      if isinstance(value, self.parent.tpe):
        self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()