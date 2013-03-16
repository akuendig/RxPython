from disposable import BooleanDisposable, Disposable
from internal import Struct
from observable import Producer
from .sink import Sink


class ToObservable(Producer):
  def __init__(self, source, scheduler):
    self.source = source
    self.scheduler = scheduler

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(ToObservable.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      it = None

      try:
        it = iter(self.parent.source)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
        return Disposable.empty()

      scheduler = self.parent.scheduler
      if scheduler.isLongRunning:
        return scheduler.scheduleLongRunningWithState(it, self.loop)
      else:
        flag = BooleanDisposable()
        scheduler.scheduleRecursiveWithState(Struct(flag=flag, it=it), self.loopRec)
        return flag

    def loopRec(self, state, recurse):
      hasNext = False
      ex = None
      current = None

      if state.flag.isDisposed:
        return

      try:
        current = next(state.it)
      except StopIteration:
        hasNext = False
      except Exception as e:
        ex = e

      if ex != None:
        self.observer.onError(ex)
        self.dispose()

      if not hasNext:
        self.observer.onCompleted()
        self.dispose()
        return

      self.observer.onNext(current)
      recurse(state)

    def loop(self, it, cancel):
      while not cancel.isDisposed:
        hasNext = False
        ex = None
        current = None

        try:
          current = next(it)
        except StopIteration:
          hasNext = False
        except Exception as e:
          ex = e

        if ex != None:
          self.observer.onError(ex)
          break

        if not hasNext:
          self.observer.onCompleted()
          break

        self.observer.onNext(current)

      self.dispose()

