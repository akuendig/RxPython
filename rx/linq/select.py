from rx.observable import Producer
import rx.linq.sink


class Select(Producer):
  def __init__(self, source, selector, withIndex):
    self.source = source
    self.selector = selector
    self.withIndex = withIndex

  def omega(self, selector):
    if self.selector != None and not self.withIndex:
      return Select(self.source, lambda x: selector(self.selector(x)))
    else:
      return Select(self, selector)

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(Select.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.index = -1

    def onNext(self, value):
      try:
        result = None
        if self.parent.withIndex:
          self.index += 1
          result = self.parent.selector(value, self.index)
        else:
          result = self.parent.selector(value)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
      else:
        self.observer.onNext(result)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()