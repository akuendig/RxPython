from rx.observable import Producer
import rx.linq.sink


class Where(Producer):
  def __init__(self, source, predicate, withIndex):
    self.source = source
    self.predicate = predicate
    self.withIndex = withIndex

  def omega(self, predicate):
    if self.withIndex:
      return Where(self, predicate)
    else:
      return Where(self.source, lambda x: self.predicate(x) and predicate(x))

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(Where.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.index = -1

    def onNext(self, value):
      shouldRun = False

      try:
        if self.parent.withIndex:
          self.index += 1
          shouldRun = self.parent.predicate(value, self.index)
        else:
          shouldRun = self.parent.predicate(value)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
        return

      if shouldRun:
        self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()