from rx.internal import Struct
from rx.observable import Producer
from .sink import Sink


class TimeStamp(Producer):
  def __init__(self, source, scheduler):
    self.source = source
    self.scheduler = scheduler

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(TimeStamp.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def onNext(self, value):
      self.observer.onNext(Struct(value=value, timestamp=self.parent.scheduler.now()))

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()