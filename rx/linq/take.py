from rx.disposable import CompositeDisposable
from rx.observable import Producer
from .sink import Sink
from threading import RLock


class TakeCount(Producer):
  def __init__(self, source, count):
    self.source = source
    self.count = count

  def omega(self, count):
    if self.count <= count:
      return self
    else:
      return TakeCount(self.source, count)

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(TakeCount.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.remaining = self.parent.count

    def onNext(self, value):
      if self.remaining > 0:
        self.remaining -= 1
        self.observer.onNext(value)

        if self.remaining == 0:
          self.observer.onCompleted()
          self.dispose()

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()


class TakeTime(Producer):
  def __init__(self, source, duration, scheduler):
    self.source = source
    self.duration = duration
    self.scheduler = scheduler

  def omega(self, duration):
    if self.duration <= duration:
      return self
    else:
      return TakeTime(self.source, duration, self.scheduler)

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(TakeTime.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.remaining = self.parent.count

    def run(self):
      self.gate = RLock()

      t = self.parent.scheduler.scheduleWithRelative(self.parent.duration, self.tick)
      d = self.parent.source.subscribeSafe(self)

      return CompositeDisposable(t, d)

    def tick(self):
      with self.gate:
        self.observer.onCompleted()
        self.dispose()

    def onNext(self, value):
      with self.gate:
        self.observer.onNext(value)

    def onError(self, exception):
      with self.gate:
        self.observer.onError(exception)
        self.dispose()

    def onCompleted(self):
      with self.gate:
        self.observer.onCompleted()
        self.dispose()
