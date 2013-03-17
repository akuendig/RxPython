from rx.internal import Struct
from rx.observable import Producer
from .sink import Sink


class TimeInterval(Producer):
  def __init__(self, source, scheduler):
    self.source = source
    self.scheduler = scheduler

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(TimeInterval.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.startTime = self.parent.scheduler.now()
      self.last = 0

      return self.parent.source.subscribeSafe(self)

    def elapsed(self):
      return self.scheduler.now() - self.startTime

    def onNext(self, value):
      now = self.elapsed()
      span = now - self.last
      self.last = now
      self.observer.onNext(Struct(value=value, interval=span))

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()