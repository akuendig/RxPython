from rx.observable import Producer
from .sink import Sink


class DistinctUntilChanged(Producer):
  def __init__(self, source, keySelector, equals):
    self.source = source
    self.keySelector = keySelector
    self.equals = equals

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
        key = self.parent.keySelector(value)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
      else:
        equal = False

        if self.hasCurrentKey:
          try:
            equal = self.parent.equals(self.currentKey, key)
          except Exception as e:
            self.observer.onError(e)
            self.dispose()

        if not self.hasCurrentKey or not equal:
          self.hasCurrentKey = True
          self.currentKey = key
          self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()