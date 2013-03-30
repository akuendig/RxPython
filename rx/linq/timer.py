from rx.concurrency import Atomic
from rx.disposable import CompositeDisposable, SingleAssignmentDisposable
from rx.observable import Producer
import rx.linq.sink


class Timer(Producer):
  def __init__(self, dueTime, isAbsolute, period, scheduler):
    self.dueTime = dueTime
    self.isAbsolute = isAbsolute
    self.period = period
    self.scheduler = scheduler

  def run(self, observer, cancel, setSink):
    if self.period == None:
      sink = self.Sink(self, observer, cancel)
      setSink(sink)
      return sink.run()
    else:
      sink = self.PeriodSink(self, observer, cancel)
      setSink(sink)
      return sink.run()

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(Timer.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      if self.parent.isAbsolute:
        self.parent.scheduler.scheduleWithAbsolute(self.parent.dueTime, self.invoke)
      else:
        self.parent.scheduler.scheduleWithRelative(self.parent.dueTime, self.invoke)

    def invoke(self):
      self.observer.onNext(0)
      self.observer.onCompleted()
      self.dispose()

  class PeriodSink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(Timer.PeriodSink, self).__init__(observer, cancel)
      self.parent = parent
      self.pendingTickCount = Atomic(0)

    def run(self):
      if self.parent.isAbsolute:
        return self.parent.scheduler.scheduleWithAbsoluteAndState(
          None,
          self.parent.dueTime,
          self.invokeStart
        )
      else:
        dueTime = self.parent.dueTime

        if dueTime == self.parent.period:
          return self.parent.scheduler.schedulePeriodicWithState(
            0,
            self.parent.period,
            self.tick
          )

        return self.parent.scheduler.scheduleWithRelativeAndState(
          None,
          dueTime,
          self.invokeStart
        )

    def tick(self, count):
      self.observer.onNext(count)
      return count + 1

    def invokeStart(self, scheduler, state):
      #
      # Notice the first call to OnNext will introduce skew if it takes significantly long when
      # using the following naive implementation:
      #
      #    Code:  base._observer.OnNext(0L);
      #           return self.SchedulePeriodicEmulated(1L, _period, (Func<long, long>)Tick);
      #
      # What we're saying here is that Observable.Timer(dueTime, period) is pretty much the same
      # as writing Observable.Timer(dueTime).Concat(Observable.Interval(period)).
      #
      #    Expected:  dueTime
      #                  |
      #                  0--period--1--period--2--period--3--period--4--...
      #                  |
      #                  +-OnNext(0L)-|
      #
      #    Actual:    dueTime
      #                  |
      #                  0------------#--period--1--period--2--period--3--period--4--...
      #                  |
      #                  +-OnNext(0L)-|
      #
      # Different solutions for this behavior have different problems:
      #
      # 1. Scheduling the periodic job first and using an AsyncLock to serialize the OnNext calls
      #    has the drawback that InvokeStart may never return. This happens when every callback
      #    doesn't meet the period's deadline, hence the periodic job keeps queueing stuff up. In
      #    this case, InvokeStart stays the owner of the AsyncLock and the call to Wait will never
      #    return, thus not allowing any interleaving of work on this scheduler's logical thread.
      #
      # 2. Scheduling the periodic job first and using a (blocking) synchronization primitive to
      #    signal completion of the OnNext(0L) call to the Tick call requires quite a bit of state
      #    and careful handling of the case when OnNext(0L) throws. What's worse is the blocking
      #    behavior inside Tick.
      #
      # In order to avoid blocking behavior, we need a scheme much like SchedulePeriodic emulation
      # where work to dispatch OnNext(n + 1) is delegated to a catch up loop in case OnNext(n) was
      # still running. Because SchedulePeriodic emulation exhibits such behavior in all cases, we
      # only need to deal with the overlap of OnNext(0L) with future periodic OnNext(n) dispatch
      # jobs. In the worst case where every callback takes longer than the deadline implied by the
      # period, the periodic job will just queue up work that's dispatched by the tail-recursive
      # catch up loop. In the best case, all work will be dispatched on the periodic scheduler.
      #

      #
      # We start with one tick pending because we're about to start doing OnNext(0L).
      #

      self.pendingTickCount.value = 1

      d = SingleAssignmentDisposable()
      self.periodic = d
      d.disposable = scheduler.schedulePeriodicWithState(1, self.parent.period, self.tock)

      try:
        self.observer.onNext(0)
      except Exception as e:
        d.dispose()
        raise e

      #
      # If the periodic scheduling job already ran before we finished dispatching the OnNext(0L)
      # call, we'll find pendingTickCount to be > 1. In this case, we need to catch up by dispatching
      # subsequent calls to OnNext as fast as possible, but without running a loop in order to ensure
      # fair play with the scheduler. So, we run a tail-recursive loop in CatchUp instead.
      #

      if self.pendingTickCount.dec() > 0:
        c = SingleAssignmentDisposable()
        c.disposable = scheduler.scheduleRecursiveWithState(1, self.catchUp)

        return CompositeDisposable(d, c)

      return d

    def tock(self, count):
      if self.pendingTickCount.inc() == 1:
        self.observer.onNext(count)
        self.pendingTickCount.dec()

      return count + 1

    def catchUp(self, count, recurse):
      try:
        self.observer.onNext(count)
      except Exception as e:
        self.periodic.dispose()
        raise e

      #
      # We can simply bail out if we decreased the tick count to 0. In that case, the Tock
      # method will take over when it sees the 0 -> 1 transition.
      #
      if self.pendingTickCount.dec() > 0:
        recurse(count + 1)

