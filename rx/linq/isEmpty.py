from rx.observable import Producer
from .sink import Sink


class IsEmpty(Producer):
  def __init__(self, source):
    self.source = source

  def run(self, observer, cancel, setSink):
    sink = self.Sink(observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, observer, cancel):
      super(IsEmpty.Sink, self).__init__(observer, cancel)
      self.currentKey = None
      self.hasCurrentKey = False

    def onNext(self, value):
      self.observer.onNext(False)
      self.observer.onCompleted()
      self.dispose()

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onNext(True)
      self.observer.onCompleted()
      self.dispose()