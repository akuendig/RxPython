from rx.disposable import CompositeDisposable
from rx.observable import Producer
from .sink import Sink


class AddRef(Producer):
  def __init__(self, source, refCount):
    self.source = source
    self.refCount = refCount

  def run(self, observer, cancel, setSink):
    d = CompositeDisposable(self.refCount.getDisposable(), cancel)

    sink = self.Sink(observer, d)
    setSink(sink)

    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, observer, cancel):
      super(AddRef.Sink, self).__init__(observer, cancel)

    def onNext(self, value):
      self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()
