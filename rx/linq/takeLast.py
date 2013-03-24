from rx.disposable import CompositeDisposable, SingleAssignmentDisposable
from rx.internal import Struct
from rx.observable import Producer
from .sink import Sink
from collections import deque


class TakeLastCount(Producer):
  def __init__(self, source, count, scheduler):
    self.source = source
    self.count = count
    self.scheduler = scheduler

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(TakeLastCount.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.queue = deque()

    def run(self):
      self.subscription = SingleAssignmentDisposable()
      self.loopDisposable = SingleAssignmentDisposable()

      self.subscription.disposable = self.parent.source.subscribeSafe(self)

      return CompositeDisposable(self.subscription, self.loopDisposable)

    def onNext(self, value):
      self.queue.append(value)

      if len(self.queue) > self.parent.count:
        self.queue.popleft()

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.subscription.dispose()

      scheduler = self.parent.scheduler
      if scheduler.isLongRunning:
        self.loopDisposable.disposable = scheduler.scheduleLongRunning(self.loop)
      else:
        self.loopDisposable.disposable = scheduler.scheduleRecursive(self.loopRec)

    def loopRec(self, recurse):
      if len(self.queue) > 0:
        self.observer.onNext(self.queue.popleft())
        recurse()
      else:
        self.observer.onCompleted()
        self.dispose()

    def loop(self, cancel):
      while not cancel.isDisposed:
        if len(self.queue) == 0:
          self.observer.onCompleted()
          break
        else:
          self.observer.onNext(self.queue.popleft())

      self.dispose()


class TakeLastTime(Producer):
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
      super(TakeLastTime.Sink, self).__init__(observer, cancel)
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

      scheduler = self.parent.scheduler
      if scheduler.isLongRunning:
        self.loop.disposable = scheduler.scheduleLongRunning(self.loop)
      else:
        self.loop.disposable = scheduler.scheduleRecursive(self.loopRec)

    def loopRec(self, recurse):
      if len(self.queue) > 0:
        self.observer.onNext(self.queue.popleft().value)
        recurse()
      else:
        self.observer.onCompleted()
        self.dispose()

    def loop(self, cancel):
      while not cancel.isDisposed:
        if len(self.queue) == 0:
          self.observer.onCompleted()
          break
        else:
          self.observer.onNext(self.queue.popleft().value)

      self.dispose()