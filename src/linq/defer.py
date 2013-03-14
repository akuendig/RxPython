from disposable import Disposable
from observable import Producer
from .sink import Sink


class Defer(Producer):
  def __init__(self, observableFactory):
    self.observableFactory = observableFactory

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  def eval(self):
    return self.observableFactory()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(Defer.Sink, self).__init__(observer, cancel)
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