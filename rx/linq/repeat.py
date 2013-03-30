from rx.observable import Producer
import rx.linq.sink


class Repeat(Producer):
  def __init__(self, value, repeatCount, scheduler):
    self.value = value
    self.repeatCount = repeatCount
    self.scheduler = scheduler

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(Repeat.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      if self.parent.scheduler.isLongRunning:
        if self.parent.repeatCount == None:
          self.parent.scheduler.scheduleLongRunning(self.loopInf)
        else:
          self.parent.scheduler.scheduleLongRunningWithState(
            self.parent.repeatCount,
            self.loop
          )
      else:
        if self.parent.repeatCount == None:
          self.parent.scheduler.scheduleRecursive(self.loopRecInf)
        else:
          self.parent.scheduler.scheduleRecursiveWithState(
            self.parent.repeatCount,
            self.loopRec
          )

    def loop(self, n, cancel):
      value = self.parent.value

      while n > 0 and not cancel.isDisposed:
        self.observer.onNext(value)
        n -= 1

      if not cancel.isDisposed:
        self.observer.onCompleted()

      self.dispose()

    def loopInf(self, cancel):
      value = self.parent.value

      while not cancel.isDisposed:
        self.observer.onNext(value)

      self.dispose()

    def loopRec(self, n, recurse):
      if n > 0:
        self.observer.onNext(self.parent.value)
        n -= 1

      if n == 0:
        self.observer.onCompleted()
        self.dispose()
        return

      recurse(n)

    def loopRecInf(self, recurse):
      self.observer.onNext(self.parent.value)
      recurse()
