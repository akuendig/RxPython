from rx.concurrency import Atomic
from rx.disposable import CompositeDisposable
from rx.observable import Producer
import rx.linq.sink


class SkipCount(Producer):
  def __init__(self, source, count):
    self.source = source
    self.count = count

  def omega(self, count):
    return SkipCount(self.source, self.count + count)

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(SkipCount.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.remaining = parent.count

    def onNext(self, value):
      if self.remaining <= 0:
        self.observer.onNext(value)
      else:
        self.remaining -= 1

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()


class SkipTime(Producer):
  def __init__(self, source, duration, scheduler):
    self.source = source
    self.duration = duration
    self.scheduler = scheduler

  def omega(self, duration):
    if duration < self.duration:
      duration = self.duration

    return SkipTime(self.source, self.duration)

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(SkipTime.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.open = Atomic(False)

    def run(self):
      t = self.parent.scheduler.scheduleWithRelative(self.parent.duration, self.tick)
      d = self.parent.source.subscribeSafe(self)

      return CompositeDisposable(t, d)

    def tick(self):
      self.open.value = True

    def onNext(self, value):
      if self.open.value:
        self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()