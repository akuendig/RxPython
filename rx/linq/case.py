from rx.disposable import Disposable
from rx.observable import Producer
import rx.linq.sink


class Case(Producer):
  def __init__(self, selector, sources, defaultSource):
    self.selector = selector
    self.sources = sources
    self.defaultSource = defaultSource

  def eval(self):
    res = self.sources.get(self.selector())

    if res != None:
      return res
    else:
      self.defaultSource

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(Case.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      result = None

      try:
        result = self.parent.eval()
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
        return Disposable.empty()

      return result.subscribeSafe(self)

    def onNext(self, value):
      self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()