from rx.observable import Producer
import rx.linq.sink


class Range(Producer):
  def __init__(self, start, count, scheduler):
    self.start = start
    self.count = count
    self.scheduler = scheduler

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(Range.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      scheduler = self.parent.scheduler

      if scheduler.isLongRunning:
        return scheduler.scheduleLongRunningWithState(
          0,
          self.loop
        )
      else:
        return scheduler.scheduleRecursiveWithState(
          0,
          self.loopRec
        )

    def loop(self, i, cancel):
      while not cancel.isDisposed and i < self.parent.count:
        self.observer.onNext(self.parent.start + i)
        i += 1

      if not cancel.isDisposed:
        self.observer.onCompleted()

      self.dispose()

    def loopRec(self, i, recurse):
      if i < self.parent.count:
        self.observer.onNext(self.parent.start + i)
        recurse(i + 1)
      else:
        self.observer.onCompleted()
        self.dispose()