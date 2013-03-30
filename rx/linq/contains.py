from rx.observable import Producer
import rx.linq.sink


class Contains(Producer):
  def __init__(self, source, value, equals):
    self.source = source
    self.value = value
    self.equals = equals

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  def getSources(self):
    return self.sources

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(Contains.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def onNext(self, value):
      res = False

      try:
        res = self.parent.equals(value, self.parent.value)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
        return

      if res:
        self.observer.onNext(True)
        self.observer.onCompleted()
        self.dispose()

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onNext(False)
      self.observer.onCompleted()
      self.dispose()