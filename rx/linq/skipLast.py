from rx.internal import Struct
from rx.observable import Producer
from .sink import Sink
from collections import deque


class SkipLastCount(Producer):
  def __init__(self, source, count):
    self.source = source
    self.count = count

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(SkipLastCount.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.queue = deque()

    def onNext(self, value):
      self.queue.append(value)

      if len(self.queue) > self.parent.count:
        self.observer.onNext(self.queue.popleft())

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()


class SkipLastTime(Producer):
  def __init__(self, source, duration, scheduler):
    self.source = source
    self.duration = duration
    self.scheduler = scheduler

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(SkipLastTime.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.startTime = self.parent.scheduler.now()

      return self.parent.subscribeSafe(self)

    def elapsed(self):
      return self.parent.scheduler.now() - self.startTime

    def onNext(self, value):
      now = self.elapsed()

      self.queue.append(Struct(value=value,timeStamp=now))

      while len(self.queue) > 0:
        current = self.queue.popleft()

        if now - current.timeStamp >= self.parent.duration:
          self.observer.onNext(current.value)
        else:
          self.queue.appendleft(current)
          break

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      now = self.elapsed()

      while len(self.queue) > 0:
        current = self.queue.popleft()

        if now - current.timeStamp >= self.parent.duration:
          self.observer.onNext(current.value)
        else:
          self.queue.appendleft(current)
          break

      self.observer.onCompleted()
      self.dispose()