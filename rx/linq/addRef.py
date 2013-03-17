from rx.disposable import CompositeDisposable
from rx.observable import Producer
from .sink import Sink


class AddRef(Producer):
  def __init__(self, source, refCount):
    self.source = source
    self.refCount = refCount

  def run(self, observer, cancel, setSink):
    d = CompositeDisposable(self.refCount.getDisposable(), cancel)

    sink = Sink(observer, d)
    setSink(sink)

    return self.source.subscribeSafe(sink)