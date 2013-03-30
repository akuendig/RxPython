from rx.disposable import CompositeDisposable, SingleAssignmentDisposable
from rx.internal import Struct
from rx.observable import Producer
import rx.linq.sink
from collections import deque


class TakeLastBufferCount(Producer):
  def __init__(self, source, count):
    self.source = source
    self.count = count

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(TakeLastBufferCount.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.queue = deque()

    def run(self):
      self.subscription = SingleAssignmentDisposable()
      self.loop = SingleAssignmentDisposable()

      self.subscription.disposable = self.parent.source.subscribeSafe(self)

      return CompositeDisposable(self.subscription, self.loop)

    def onNext(self, value):
      self.queue.append(value)

      if len(self.queue) > self.parent.count:
        self.queue.popleft()

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      res = list(self.queue)

      self.observer.onNext(res)
      self.observer.onCompleted()
      self.dispose()


class TakeLastBufferTime(Producer):
  def __init__(self, source, duration, scheduler):
    self.source = source
    self.duration = duration
    self.scheduler = scheduler

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(TakeLastBufferTime.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.subscription = SingleAssignmentDisposable()
      self.loop = SingleAssignmentDisposable()

      self.startTime = self.parent.scheduler.now()
      self.subscription.disposable = self.parent.source.subscribeSafe(self)

      return CompositeDisposable(self.subscription, self.loop)

    def elapsed(self):
      return self.parent.scheduler.now() - self.startTime

    def trim(self, now):
      while len(self.queue) > 0:
        current = self.queue.popleft()

        if current.interval < self.parent.duration:
          self.queue.appendleft(current)
          break

    def onNext(self, value):
      now = self.elapsed()

      self.queue.append(Struct(value=value,interval=now))
      self.trim(now)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.subscription.dispose()

      now = self.elapsed()
      self.trim(now)

      res = list([x.value for x in self.queue])

      self.observer.onNext(res)
      self.observer.onCompleted()
      self.dispose()