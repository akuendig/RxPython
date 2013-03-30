from rx.observable import Producer
import rx.linq.sink


class Distinct(Producer):
  def __init__(self, source, keySelector):
    self.source = source
    self.keySelector = keySelector

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(Distinct.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.hashSet = set()

    def onNext(self, value):
      try:
        key = self.parent.keySelector(value)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
      else:
        if key in self.hashSet:
          return
        else:
          self.hashSet.add(key)
          self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()