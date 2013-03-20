from rx.observable import Producer
from .sink import Sink


class SingleAsync(Producer):
  def __init__(self, source, predicate, throwOnEmpty, defaultValue):
    self.source = source
    self.predicate = predicate
    self.throwOnEmpty = throwOnEmpty
    self.defaultValue = defaultValue

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(SingleAsync.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.value = self.parent.defaultValue
      self.hasValue = False

    def onNext(self, value):
      b = False

      try:
        b = self.parent.predicate(value)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()

      if b:
        if self.hasValue:
          self.observer.onError(Exception("Invalid operation, more than one element in observable"))
          self.dispose()
          return

        self.value = value
        self.hasValue = True

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      if not self.hasValue and self.parent.throwOnEmpty:
        self.observer.onError(Exception("Invalid operation, no elements in observable"))
      else:
        self.observer.onNext(self.value)
        self.observer.onCompleted()

      self.dispose()