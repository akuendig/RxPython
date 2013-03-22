from rx.observable import Producer
from .sink import Sink


class ElementAt(Producer):
  def __init__(self, source, index, throwOnEmpty, default):
    self.source = source
    self.index = index
    self.throwOnEmpty = throwOnEmpty
    self.default = default

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(ElementAt.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.i = self.parent.index

    def onNext(self, value):
      if self.i == 0:
        self.observer.onNext(value)
        self.observer.onCompleted()
        self.dispose()

      self.i -= 1

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      if self.parent.throwOnEmpty:
        self.observer.onError(Exception("Argument out of range: index"))
      else:
        self.observer.onNext(self.parent.default)
        self.observer.onCompleted()

      self.dispose()