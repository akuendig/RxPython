from rx.observable import Producer
import rx.linq.sink


class Concat(Producer):
  def __init__(self, sources):
    self.sources = sources

  def run(self, observer, cancel, setSink):
    sink = self.Sink(observer, cancel)
    setSink(sink)
    return sink.run(self.sources)

  def getSources(self):
    return self.sources

  class Sink(rx.linq.sink.ConcatSink):
    def __init__(self, observer, cancel):
      super(Concat.Sink, self).__init__(observer, cancel)

    def onNext(self, value):
      self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()