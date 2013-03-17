from rx.observable import Producer
from .sink import Sink


class AsObservable(Producer):
  def __init__(self, source, predicate):
    self.source = source
    self.predicate = predicate

  def omega(self):
    return self

  def eval(self):
    return self.source

  def run(self, observer, cancel, setSink):
    sink = self.Sink(observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, observer, cancel):
      super(AsObservable.Sink, self).__init__(observer, cancel)

    def onNext(self, value):
      self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()