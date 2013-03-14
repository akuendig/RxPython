from observable import Producer
from .sink import Sink


class ToList(Producer):
  def __init__(self, source):
    self.source = source

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(ToList.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.list = []

    def onNext(self, value):
      self.list.append(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onNext(self.list)
      self.observer.onCompleted()
      self.dispose()