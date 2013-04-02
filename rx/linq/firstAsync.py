from rx.exceptions import InvalidOperationException
from rx.observable import Producer
import rx.linq.sink


class FirstAsync(Producer):
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
      super(FirstAsync.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def onNext(self, value):
      try:
        b = self.parent.predicate(value)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
      else:
        if b:
          self.observer.onNext(value)
          self.observer.onCompleted()
          self.dispose()

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      if self.parent.throwOnEmpty:
        self.observer.onError(InvalidOperationException("No elements in observable"))
      else:
        self.observer.onNext(self.parent.defaultValue)
        self.observer.onCompleted()

      self.dispose()