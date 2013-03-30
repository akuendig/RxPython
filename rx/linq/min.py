from rx.observable import Producer
import rx.linq.sink


class Min(Producer):
  def __init__(self, source, compareTo):
    self.source = source
    self.compareTo = compareTo

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(Min.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.lastValue = None
      self.hasValue = False

    def onNext(self, value):
      if value != None:
        if not self.hasValue:
          self.lastValue = value
          self.hasValue = True
        else:
          try:
            if self.parent.compareTo(value, self.lastValue) < 0:
              self.lastValue = value
          except Exception as e:
            self.observer.onError(e)
            self.dispose()

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      if not self.hasValue:
        self.observer.onError(Exception("Invalid operation, no elements in observable"))
      else:
        self.observer.onNext(self.lastValue)
        self.observer.onCompleted()
      self.dispose()