from rx.exceptions import InvalidOperationException
from rx.observable import Producer
import rx.linq.sink


class LastAsync(Producer):
  def __init__(self, source, predicate, throwOnEmpty, defaultValue):
    self.source = source
    self.predicate = predicate
    self.throwOnEmpty = throwOnEmpty
    self.defaultValue = defaultValue

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(LastAsync.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.value = self.parent.defaultValue
      self.hasValue = False

    def onNext(self, value):
      try:
        if self.parent.predicate(value):
          self.value = value
          self.hasValue = True
      except Exception as e:
        self.observer.onError(e)
        self.dispose()

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      if not self.hasValue and self.parent.throwOnEmpty:
        self.observer.onError(InvalidOperationException("No elements in observable"))
      else:
        self.observer.onNext(self.value)
        self.observer.onCompleted()

      self.dispose()