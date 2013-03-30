from rx.observable import Producer
import rx.linq.sink


class OnErrorResumeNext(Producer):
  def __init__(self, sources):
    self.sources = sources

  def run(self, observer, cancel, setSink):
    sink = self.Sink(observer, cancel)
    setSink(sink)
    return sink.run(self.sources)

  class Sink(rx.linq.sink.TailRecursiveSink):
    def __init__(self, observer, cancel):
      super(OnErrorResumeNext.Sink, self).__init__(observer, cancel)
      self.currentKey = None
      self.hasCurrentKey = False

    def extract(self, sources):
      if isinstance(sources, OnErrorResumeNext):
        return sources.sources
      else:
        return None

    def onNext(self, value):
      self.observer.onNext(value)

    def onError(self, exception):
      self.recurse()

    def onCompleted(self):
      self.recurse()
