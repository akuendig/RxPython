from rx.observable import Producer
from .sink import Sink


class MinBy(Producer):
  def __init__(self, source, keySelector, compareTo):
    self.source = source
    self.keySelector = keySelector
    self.compareTo = compareTo

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(MinBy.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.hasValue = False
      self.lastKey = None
      self.list = []

    def onNext(self, value):
      key = None
      comparison = 0

      try:
        key = self.parent.keySelector(value)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
        return

      if not self.hasValue:
        self.hasValue = True
        self.lastKey = key
      else:
        try:
          comparison = self.parent.compareTo(key, self.lastKey)
        except Exception as e:
          self.observer.onError(e)
          self.dispose()
          return

      if comparison < 0:
        self.lastKey = key
        self.list.clear()

      if comparison <= 0:
        self.list.append(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onNext(self.list)
      self.observer.onCompleted()
      self.dispose()