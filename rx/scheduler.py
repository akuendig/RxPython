from rx.concurrency import Atomic
from rx.disposable import AsyncLock, Disposable, BooleanDisposable, CompositeDisposable, SingleAssignmentDisposable
from rx.internal import defaultNow, defaultSubComparer
import threading
from concurrent.futures import ThreadPoolExecutor
from functools import partial as bind
from queue import Empty, PriorityQueue
from threading import Thread, Timer, RLock
from time import sleep


class Scheduler(object):
  """Provides a set of static properties to access commonly
  used Schedulers."""

  @staticmethod
  def invokeAction(scheduler, action):
    action()
    return Disposable.empty()

  @staticmethod
  def invokeRecImmediate(scheduler, pair):
    state = pair[0]
    action = pair[1]

    scheduled = RecursiveScheduledFunction(action, scheduler)
    scheduled.run(state)

    return scheduled.group

  @staticmethod
  def invokeRecDate(scheduler, pair, method):
    state = pair[0]
    action = pair[1]

    scheduled = RecursiveScheduledFunction(action, scheduler, method)
    scheduled.run(state)

    return scheduled.group

  @staticmethod
  def now():
    return defaultNow()

  @staticmethod
  def normalize(timeSpan):
    if timeSpan < 0:
      return 0
    else:
      return timeSpan

  def catchException(self, handler):
    return CatchScheduler(self, handler)

  # longrunning scheduling
  # action takes as parameter: state and cancel
  # and returns None
  def scheduleLongRunning(self, action):
    return self.scheduleLongRunningWithState(None, lambda s, cancel: action(cancel))

  ## commented out such that one can test if a scheduler can schedule long running
  # def scheduleLongRunningWithState(self, state, action):
  #   raise NotImplementedError()
  @property
  def isLongRunning(self):
    return hasattr(self, "scheduleLongRunningWithState")

  # periodic scheduling
  # action takes as parameter: state
  # and returns: state
  def schedulePeriodic(self, period, action):
    return self.schedulePeriodicWithState(None, period, lambda s: action())

  def schedulePeriodicWithState(self, state, period, action):
    def gated():
      state = action(state)

    timer = PeriodicTimer(period, gated)

    return timer.start()

  # once scheduling
  # action takes as parameter: scheduler, state
  # and returns: disposable to cancel
  def schedule(self, action):
    return self._scheduleCore(action, Scheduler.invokeAction)

  def scheduleWithState(self, state, action):
    return self._scheduleCore(state, action)

  def scheduleWithRelative(self, dueTime, action):
    return self._scheduleRelativeCore(action, dueTime, Scheduler.invokeAction)

  def scheduleWithRelativeAndState(self, state, dueTime, action):
    return self._scheduleRelativeCore(state, dueTime, action)

  def scheduleWithAbsolute(self, dueTime, action):
    return self._scheduleAbsoluteCore(action, dueTime, Scheduler.invokeAction)

  def scheduleWithAbsoluteAndState(self, state, dueTime, action):
    return self._scheduleAbsoluteCore(state, dueTime, action)

  # recursive scheduling
  # action takes as parameter: continuation([state], [period])
  # and returns: None
  def scheduleRecursive(self, action):
    return self.scheduleRecursiveWithState(
      None,
      lambda _, _continuation: action(lambda: _continuation(None))
    )

  def scheduleRecursiveWithState(self, state, action):
    return self.scheduleWithState((state, action), Scheduler.invokeRecImmediate)

  def scheduleRecursiveWithRelative(self, dueTime, action):
    return self.scheduleRecursiveWithRelativeAndState(
      None,
      dueTime,
      lambda _, _continuation: action(lambda dt: _continuation(None, dt))
    )

  def scheduleRecursiveWithRelativeAndState(self, state, dueTime, action):
    return self._scheduleRelativeCore(
      (state, action),
      dueTime,
      lambda s, p: Scheduler.invokeRecDate(s, p, 'scheduleWithRelativeAndState')
    )

  def scheduleRecursiveWithAbsolute(self, dueTime, action):
    return self.scheduleRecursiveWithAbsoluteAndState(
      action,
      lambda _action, _self: _action(lambda: _self(_action))
    )

  def scheduleRecursiveWithAbsoluteAndState(self, state, dueTime, action):
    return self._scheduleAbsoluteCore(
      (state, action),
      dueTime,
      lambda s, p: Scheduler.invokeRecDate(s, p, 'scheduleWithAbsoluteAndState')
    )

  def _scheduleCore(self, state, action):
    raise NotImplementedError()

  def _scheduleRelativeCore(self, state, dueTime, action):
    raise NotImplementedError()

  def _scheduleAbsoluteCore(self, state, dueTime, action):
    raise NotImplementedError()


class CatchWrapper:
  def __init__(self, parent, action):
    self.parent = parent
    self.action = action

  def __call__(self, _self, _state):
    try:
      return self.action(self.parent._getRecursiveWrapper(_self), _state)
    except Exception as e:
      if not self.parent._handler(e): raise e
      return Disposable.empty()


class CatchScheduler(Scheduler):
  def __init__(self, scheduler, handler):
    super(CatchScheduler, self).__init__()

    self._scheduler = scheduler
    self._handler = handler
    self._recursiveOriginal = None
    self._recursiveWrapper = None

    self.lock = RLock()

  def now(self):
    return self._scheduler.now()

  def _scheduleCore(self, state, action):
    return self._scheduler.scheduleWithState(state, self._wrap(action))

  def _scheduleRelativeCore(self, state, dueTime, action):
    return self._scheduler.scheduleWithRelativeAndState(state, dueTime, self._wrap(action))

  def _scheduleAbsoluteCore(self, state, dueTime, action):
    return self._scheduler.scheduleWithAbsoluteAndState(state, dueTime, self._wrap(action))

  def _clone(self, scheduler):
    return CatchScheduler(scheduler, self._handler)

  def _wrap(self, action):
    return CatchWrapper(self, action)

  def _getRecursiveWrapper(self, scheduler):
    with self.lock:
      if self._recursiveOriginal != scheduler:
        self._recursiveOriginal = scheduler

        wrapper = self._clone(scheduler)
        wrapper._recursiveOriginal = scheduler
        wrapper._recursiveWrapper = wrapper

        self._recursiveWrapper = wrapper

    return self._recursiveWrapper

  def schedulePeriodicWithState(self, state, period, action):
    failed = False
    failureLock = RLock
    d = SingleAssignmentDisposable()

    def scheduled(_state):
      with failureLock:
        nonlocal failed

        if failed:
          return None

        try:
          return action(_state)
        except Exception as e:
          failed = True

          if not self.handler(e):
            raise e

          d.dispose()

          return None

    d.setDisposable(
      self._scheduler.schedulePeriodicWithState(
        state,
        period,
        scheduled
    ))

    return d


class CurrentThreadScheduler(Scheduler):
  """Represents a Scheduler that schedules its items into a queue which
  allows cooperative concurrency because the current scheduled function
  always runs to completion before a possibly new scheduled function executes.
  See ImmediateScheduler for problems that this would impose."""
  def __init__(self):
    super(CurrentThreadScheduler, self).__init__()

  _local = threading.local()

  def isScheduleRequired(self):
    return self._queue == None

  def ensureTrampoline(self, action):
    if self.scheduleRequired():
      return self.schedule(action)
    else:
      return action()

  def _queue():
    def fget(self):
      if not hasattr(self._local, 'reactive_extensions_current_thread_queue'):
        self._local.reactive_extensions_current_thread_queue = None

      return self._local.reactive_extensions_current_thread_queue
    def fset(self, value):
      self._local.reactive_extensions_current_thread_queue = value
    def fdel(self):
      del self._local.reactive_extensions_current_thread_queue
    return locals()
  _queue = property(**_queue())

  def _init(self):
    self._queue = PriorityQueue(4)

  def _dispose(self):
    self._queue = None

  def _run(self):
    while not self._queue.empty():
      item = self._queue.get()

      if item.isCancelled():
        continue

      dt = item.dueTime - Scheduler.now()
      if dt > 0:
        sleep(dt)

      if not item.isCancelled():
        item.invoke()

  def _scheduleCore(self, state, action):
    return self.scheduleWithRelativeAndState(state, 0, action)

  def _scheduleRelativeCore(self, state, dueTime, action):
    dt = self.now() + Scheduler.normalize(dueTime)
    si = ScheduledItem(self, state, action, dt)

    if self._queue == None:
      self._init()

      try:
        self._queue.put(si)
        self._run()
      finally:
        self._dispose()
    else:
      self._queue.put(si)

    return si.disposable

  def _scheduleAbsoluteCore(self, state, dueTime, action):
    return self.scheduleWithRelativeAndState(state, dueTime - self.now(), action)


class DefaultScheduler(Scheduler):
  """Represents a Scheduler that schedules its items on
  a task/thread pool"""
  def __init__(self):
    super(DefaultScheduler, self).__init__()
    self.pool = ThreadPoolExecutor(max_workers=16)

  def _scheduleCore(self, state, action):
    d = SingleAssignmentDisposable()

    def scheduled():
      if not d.isDisposed:
        d.disposable = action(self, state)

    future = self.pool.submit(scheduled)
    cancel = Disposable.create(future.cancel)

    return CompositeDisposable(d, cancel)

  def _scheduleRelativeCore(self, state, dueTime, action):
    dt = Scheduler.normalize(dueTime)

    if dt == 0:
      return self.scheduleWithState(state, action)

    d = SingleAssignmentDisposable()

    def scheduled():
      if not d.isDisposed:
        d.disposable = action(self, state)

    timer = Timer(dt, scheduled)
    cancel = Disposable.create(timer.cancel)

    return CompositeDisposable(d, cancel)

  def _scheduleAbsoluteCore(self, state, dueTime, action):
    return self.scheduleWithRelativeAndState(state, dueTime - self.now(), action)

  def schedulePeriodicWithState(self, state, interval, action):
    gate = AsyncLock()

    def gated():
      state = action(state)

    timer = PeriodicTimer(interval, lambda: gate.wait(gated))
    cancel = timer.start()

    return CompositeDisposable(cancel, gate)

  def scheduleLongRunningWithState(self, state, action):
    cancel = BooleanDisposable()

    def run():
      action(state, cancel)
    thread = Thread(target=run)
    thread.start()

    return cancel


class VirtualTimeScheduler(Scheduler):
  """Creates a new virtual time scheduler with the
  specified initial clock value and absolute time comparer."""

  def __init__(self, clock, comparer):
    super(VirtualTimeScheduler, self).__init__()
    self.clock = clock
    self.comparer = comparer
    self.isEnabled = False
    self.queue = PriorityQueue(1024)

  def now(self):
    return self.toDateTimeOffset(self.clock)

  def _scheduleCore(self, state, action):
    return self.scheduleAbsoluteWithState(state, self.clock, action)

  def _scheduleRelativeCore(self, state, dueTime, action):
    return self.scheduleRelativeWithState(state, self.toRelative(dueTime), action)

  def _scheduleAbsoluteCore(self, state, dueTime, action):
    return self.scheduleRelativeWithState(state, self.toRelative(dueTime - self.now()), action)

  def schedulePeriodicWithState(self, state, period, action):
    raise NotImplementedError()

  def scheduleRelativeWithState(self, state, dueTime, action):
    runAt = self.add(self.clock, dueTime)
    return self.scheduleAbsoluteWithState(state, runAt, action)

  def scheduleRelative(self, dueTime, action):
    return self.scheduleRelativeWithState(action, dueTime, Scheduler.invokeAction)

  def scheduleAbsolute(self, dueTime, action):
    return self.scheduleAbsoluteWithState(action, dueTime, Scheduler.invokeAction)

  def scheduleAbsoluteWithState(self, state, dueTime, action):
    si = ScheduledItem(self, state, action, dueTime, self.comparer)

    self.queue.put(si)

    return si.disposable

  def start(self, until=None):
    if not self.isEnabled:
      self.isEnabled = True

      while self.isEnabled:
        next = self.getNext()
        nextIsTooLate = until != None and self.comparer(next.dueTime, until) > 0

        if next == None or nextIsTooLate:
          self.queue.put(next)
          self.isEnabled = False
        else:
          if self.comparer(next.dueTime, self.clock) > 0:
            self.clock = next.dueTime

          next.invoke()

  def stop(self):
    self.isEnabled = False

  def advanceTo(self, time):
    dueToClock = self.comparer(time, self.clock)

    if dueToClock < 0:
      raise Exception('Argument out of range')

    if dueToClock == 0:
      return

    self.start(time)

  def advanceBy(self, time):
    return self.advanceTo(self.add(self.clock, time))

  def sleep(self, time):
    until = self.add(self.clock, time)

    if self.comparer(self.clock, until) >= 0:
      raise Exception('Argument out of range')

    self.clock = until

  def getNext(self):
    while True:
      next = None

      try:
        next = self.queue.get(True, 0)
      except Empty:
        return None

      if next.isCancelled():
        continue
      else:
        return next


class HistoricalScheduler(VirtualTimeScheduler):
  """Provides a virtual time scheduler that uses number for
  absolute time and number for relative time."""
  def __init__(self, initialClock = 0, comparer = defaultSubComparer):
    super(HistoricalScheduler, self).__init__(initialClock, comparer)
    self.clock = initialClock
    self.cmp = comparer

  def add(self, absolute, relative):
    return absolute + relative

  def toDateTimeOffset(self, absolute):
    return absolute

  def toRelative(self, timeSpan):
    return timeSpan


class ImmediateScheduler(Scheduler):
  """This scheduler immediatly run scheduled functions and if it schedules
  relative, then it waits for this relative time. This can possibly deadlock
  if a scheduled function schedules an other function but the other function
  needs the current function to complete before finishing.
  To avoid this use CurrentThreadScheduler."""
  def __init__(self):
    super(ImmediateScheduler, self).__init__()

  def _scheduleCore(self, state, action):
    return action(self.AsyncLockScheduler(), state)

  def _scheduleRelativeCore(self, state, dueTime, action):
    dt = Scheduler.normalize(dueTime)

    if dt > 0:
      sleep(dt)

    return action(self.AsyncLockScheduler(), state)

  def _scheduleAbsoluteCore(self, state, dueTime, action):
    return self.scheduleWithRelativeAndState(state, dueTime - self.now(), action)

  class AsyncLockScheduler(Scheduler):
    def __init__(self):
      super(ImmediateScheduler.AsyncLockScheduler, self).__init__()
      self.gate = None

    def _scheduleCore(self, state, action):
      m = SingleAssignmentDisposable()

      def gated():
        if not m.isDisposed:
          m.disposable = action(self, state)

      if self.gate == None:
        self.gate = AsyncLock()

      self.gate.wait(gated)

      return m

    def _scheduleRelativeCore(self, state, dueTime, action):
      m = SingleAssignmentDisposable()
      now = Scheduler.now()

      def gated():
        if not m.isDisposed:
          elapsed = Scheduler.now() - now
          dt = Scheduler.normalize(dueTime - elapsed)

          if dt > 0:
            sleep(dt)

          if not m.isDisposed:
            m.disposable = action(self, state)

      if self.gate == None:
        self.gate = AsyncLock()

      self.gate.wait(gated)

      return m

    def _scheduleAbsoluteCore(self, state, dueTime, action):
      return self.scheduleWithRelativeAndState(state, dueTime - self.now(), action)


class RecursiveScheduledFunction(object):
  def __init__(self, action, scheduler, method = None):
    self.action = action
    self.schedule = scheduler if method == None else scheduler[method]
    self.group = CompositeDisposable()
    self.lock = RLock()

    if method == None:
      self.schedule = scheduler.scheduleWithState
    else:
      self.schedule = bind(getattr(scheduler, method), scheduler)

  def run(self, state):
    self.action(state, self.actionCallback)

  def actionCallback(self, newState, dueTime = None):
    self.isDone = False
    self.isAdded = False

    if dueTime == None:
      self.cancel = self.schedule(
        newState,
        self.schedulerCallback
      )
    else:
      self.cancel = self.schedule(
        newState,
        dueTime,
        self.schedulerCallback
      )

    with self.lock:
      if not self.isDone:
        self.group.add(self.cancel)
        self.isAdded = True

  def schedulerCallback(self, scheduler, state):
    with self.lock:
      if self.isAdded:
        self.group.remove(self.cancel)
      else:
        self.isDone = True

    self.run(state)

    return Disposable.empty()


class PeriodicTimer(object):
  """A timer that runs every interval seconds, can shift in time"""
  def __init__(self, interval, action):
    super(PeriodicTimer, self).__init__()
    self.interval = interval
    self.action = action
    self.timerDisposable = SerialDisposable()

  def start(self):
    timer = Timer(self.interval, self._execute)

    self.timerDisposable.disposable = Disposable.create(timer.cancel)

    timer.start()

    return self.timerDisposable

  def cancel(self):
    self.timerDisposable.dispose()

  def _execute(self):
    self.action()
    self.run()


class ScheduledItem(object):
  """Provides a scheduled cancelable item with state and comparer"""
  def __init__(self, scheduler, state, action, dueTime, comparer = defaultSubComparer):
    self.scheduler = scheduler
    self.state = state
    self.action = action
    self.dueTime = dueTime
    self.comparer = comparer
    self.disposable = SingleAssignmentDisposable()

  def invoke(self):
    self.disposable.disposable = self.invokeCore()

  def isCancelled(self):
    return self.disposable.isDisposed

  def invokeCore(self):
    return self.action(self.scheduler, self.state)

  def compareTo(self, other):
    return self.comparer(self.dueTime, other.dueTime)

  def __lt__(self, other):
    return self.compareTo(other) < 0


immediateScheduler = ImmediateScheduler()
Scheduler.immediate = immediateScheduler

currentThreadScheduler = CurrentThreadScheduler()
Scheduler.currentThread = currentThreadScheduler

defaultScheduler = DefaultScheduler()
Scheduler.default = defaultScheduler

Scheduler.constantTimeOperations = immediateScheduler
Scheduler.tailRecursion = immediateScheduler
Scheduler.iteration = currentThreadScheduler
Scheduler.timeBasedOperation = defaultScheduler
Scheduler.asyncConversions = defaultScheduler
