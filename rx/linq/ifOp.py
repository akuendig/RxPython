from rx.disposable import Disposable
from rx.observable import Producer
from .sink import Sink


class If(Producer):
  def __init__(self, condition, thenSource, elseSource):
    self.condition = condition
    self.thenSource = thenSource
    self.elseSource = elseSource

  def eval(self):
    if self.condition():
      return self.thenSource
    else:
      return self.elseSource

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(If.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      try:
        result = self.parent.eval()
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
        return Disposable.empty()
      else:
        return result.subscribeSafe(self)

    def onNext(self, value):
      self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()