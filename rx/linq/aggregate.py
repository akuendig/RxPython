from rx.observable import Producer
import rx.linq.sink


class Aggregate(Producer):
  def __init__(self, source, seed, accumulator, resultSelector):
    self.source = source
    self.seed = seed
    self.accumulator = accumulator
    self.resultSelector = resultSelector

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(Aggregate.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.accumulation = parent.seed

    def onNext(self, value):
      try:
        self.accumulation = self.parent.accumulator(self.accumulation, value)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      result = None

      try:
        result = self.parent.resultSelector(self.accumulation)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
        return

      self.observer.onNext(result)
      self.observer.onCompleted()
      self.dispose()