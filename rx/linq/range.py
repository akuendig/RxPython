from observable import Producer
from .sink import Sink


class Range(Producer):
  def __init__(self, start, count, scheduler):
    self.start = start
    self.count = count
    self.scheduler = scheduler

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(Range.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      if self.parent.scheduler.isLongRunning:
        return self.parent.scheduleLongRunningWithState(0, self.loop)
      else:
        return self.parent.scheduleRecursiveWithState(0, self.loopRec)

    def loop(self, i, cancel):
      while not cancel.isDisposed and i < self.parent.count:
        self.observer.onNext(self.parent.start + i)
        i += 1

      if not cancel.isDisposed:
        self.observer.onCompleted()

      self.dispose()

    def loopRec(self, i, recurse):
      if i < self.parent.count:
        self.observer.onNext(i)
        recurse(i + 1)
      else:
        self.observer.onCompleted()
        self.dispose()