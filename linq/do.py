from observable import Producer
from .sink import Sink


class Do(Producer):
  def __init__(self, source, onNext, onError, onCompleted):
    self.source = source
    self.doOnNext = onNext
    self.doOnError = onError
    self.doOnCompleted = onCompleted

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(Do.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def onNext(self, value):
      try:
        self.parent.onNext(value)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
      else:
        self.observer.onNext(value)

    def onError(self, exception):
      try:
        self.parent.onError(exception)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
      else:
        self.observer.onNext(exception)
        self.dispose()

    def onCompleted(self):
      try:
        self.parent.onCompleted()
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
      else:
        self.observer.onCompleted()
        self.dispose()