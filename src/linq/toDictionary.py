from observable import Producer
from .sink import Sink


class ToDictionary(Producer):
  def __init__(self, source, keySelector, elementSelector):
    self.source = source
    self.keySelector = keySelector
    self.elementSelector = elementSelector

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(ToDictionary.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.dictionary = {}

    def onNext(self, value):
      try:
        self.dictionary.add(
          self.parent.keySelector(value),
          self.parent.elementSelector(value)
        )
      except Exception as e:
        self.observer.onError(e)
        self.dispose()

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onNext(self.dictionary)
      self.observer.onCompleted()
      self.dispose()