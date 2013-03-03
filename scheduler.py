from disposable import Disposable, CompositeDisposable, SingleAssignmentDisposable
from functools import partial as bind
from concurrency import Atomic
from internal import defaultNow, defaultSubComparer
import threading
from threading import Timer, RLock
from queue import PriorityQueue
from time import sleep


class Scheduler:
  """Provides a set of static properties to access commonly
  used Schedulers."""

  def __init__(self, now, schedule, scheduleRelative, scheduleAbsolute):
    self.now = now
    self._schedule = schedule
    self._scheduleRelative = scheduleRelative
    self._scheduleAbsolute = scheduleAbsolute

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
  # and return None
  def scheduleLongRunning(self, action):
    return self.scheduleLongRunningWithState(None, lambda s, cancel: action(cancel))

  def scheduleLongRunningWithState(self, state, action):
    raise NotImplementedError()

  # periodic scheduling
  # action takes as parameter: state
  # and return: state
  def schedulePeriodic(self, period, action):
    return self.schedulePeriodicWithState(None, period, lambda s: action())

  def schedulePeriodicWithState(self, state, period, action):
    timer = PeriodicTimerWithState(period, action, state)
    return timer.start()

  # once scheduling
  # action takes as parameter: scheduler, state
  # and return: disposable to cancel
  def schedule(self, action):
    return self._schedule(action, Scheduler.invokeAction)

  def scheduleWithState(self, state, action):
    return self._schedule(state, action)

  def scheduleWithRelative(self, dueTime, action):
    return self._scheduleRelative(action, dueTime, Scheduler.invokeAction)

  def scheduleWithRelativeAndState(self, state, dueTime, action):
    return self._scheduleRelative(state, dueTime, action)

  def scheduleWithAbsolute(self, dueTime, action):
    return self._scheduleAbsolute(action, dueTime, Scheduler.invokeAction)

  def scheduleWithAbsoluteAndState(self, state, dueTime, action):
    return self._scheduleAbsolute(state, dueTime, action)

  # recursive scheduling
  def scheduleRecursive(self, action):
    return self.scheduleRecursiveWithState(
      action,
      lambda _action, _self: _action(lambda: _self(_action))
    )

  def scheduleRecursiveWithState(self, state, action):
    return self.scheduleWithState((state, action), Scheduler.invokeRecImmediate)

  def scheduleRecursiveWithRelative(self, dueTime, action):
    return self.scheduleRecursiveWithRelativeAndState(
      action,
      dueTime,
      lambda _action, _self: _action(lambda dt: _self(_action, dt))
    )

  def scheduleRecursiveWithRelativeAndState(self, state, dueTime, action):
    return self._scheduleRelative(
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
    return self._scheduleRelative(
      (state, action),
      dueTime,
      lambda s, p: Scheduler.invokeRecDate(s, p, 'scheduleWithAbsoluteAndState')
    )


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
  def _localNow(self):
    return self._scheduler.now()

  def _scheduleNow(self, state, action):
    return self._scheduler.scheduleWithState(state, self._wrap(action))

  def _scheduleRelative(self, state, dueTime, action):
    return self._scheduler.scheduleWithRelativeAndState(state, dueTime, self._wrap(action))

  def _scheduleAbsolute(self, state, dueTime, action):
    return self._scheduler.scheduleWithAbsoluteAndState(state, dueTime, self._wrap(action))

  def __init__(self, scheduler, handler):
    super(CatchScheduler, self).__init__(
      self._localNow,
      self._scheduleNow,
      self._scheduleRelative,
      self._scheduleAbsolute
    )

    self._scheduler = scheduler
    self._handler = handler
    self._recursiveOriginal = None
    self._recursiveWrapper = None

    self.lock = RLock()

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
  def __init__(self):
    super(CurrentThreadScheduler, self).__init__(
      defaultNow,
      self._scheduleNow,
      self._scheduleRelative,
      self._scheduleAbsolute
    )

  def scheduleRequired(self):
    return self._queue == None

  def ensureTrampoline(self, action):
    if self.scheduleRequired():
      return self.schedule(action)
    else:
      return action()

  def _queue():
    def fget(self):
      if not hasattr(threading.local(), 'reactive_extensions_current_thread_queue'):
        threading.local().reactive_extensions_current_thread_queue = None

      return threading.local().reactive_extensions_current_thread_queue
    def fset(self, value):
      threading.local().reactive_extensions_current_thread_queue = value
    def fdel(self):
      del threading.local().reactive_extensions_current_thread_queue
    return locals()
  _queue = property(**_queue())

  def _init(self):
    self._queue = PriorityQueue(4)

  def _dispose(self):
    self._queue = None

  def _run(self):
    while self._queue.not_empty():
      item = self._queue.get()

      if item.isCancelled():
        continue

      sleep(item.dueTime - Scheduler.now())

      if not item.isCancelled():
        item.invoke()

  def _scheduleNow(self, state, action):
    return self.scheduleWithRelativeAndState(state, 0, action)

  def _scheduleRelative(self, dueTime, action):
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

  def _scheduleAbsolute(self, state, dueTime, action):
    return self.scheduleWithRelativeAndState(state, dueTime - self.now(), action)


class VirtualTimeScheduler(Scheduler):
  """Creates a new virtual time scheduler with the
  specified initial clock value and absolute time comparer."""

  def _localNow(self):
    return self.toDateTimeOffset(self.clock)

  def _scheduleNow(self, state, action):
    return self.scheduleAbsoluteWithState(state, self.clock, action)

  def _scheduleRelative(self, state, dueTime, action):
    return self.scheduleRelativeWithState(state, self.toRelative(dueTime), action)

  def _scheduleAbsolute(self, state, dueTime, action):
    return self.scheduleRelativeWithState(state, self.toRelative(dueTime - self.now()), action)

  def __init__(self, clock, comparer):
    super(VirtualTimeScheduler, self).__init__(
      self._localNow,
      self._scheduleNow,
      self._scheduleRelative,
      self._scheduleAbsolute
    )
    self.clock = clock
    self.comparer = comparer
    self.isEnabled = False
    self.queue = PriorityQueue(1024)

  def schedulePeriodicWithState(self, state, period, action):
    raise Exception('Not implemented')

  def scheduleRelativeWithState(self, state, dueTime, action):
    runAt = self.add(self.clock, dueTime)
    return self.scheduleAbsoluteWithState(state, runAt, action)

  def scheduleRelative(self, dueTime, action):
    return self.scheduleRelativeWithState(action, dueTime, Scheduler.invokeAction)

  def scheduleAbsolute(self, dueTime, action):
    return self.scheduleAbsoluteWithState(action, dueTime, Scheduler.invokeAction)

  def scheduleAbsoluteWithState(self, state, dueTime, action):
    si = ScheduledItem(self, state, run, dueTime, self.comparer)

    self.queue.put(si)

    return si.disposable

  def start(self, until):
    if not self.isEnabled:
      self.isEnabled = True

      while self.isEnabled:
        next = self.getNext()
        nextIsTooLate = until != None and self.comparer(next.dueTime, until) > 0

        if next == None or nextIsTooLate:
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
      next = self.queue.get_nowait()

      if next == None:
        return None
      elif next.isCancelled():
        continue
      else:
        return next


class HistoricalScheduler(VirtualTimeScheduler):
  """Provides a virtual time scheduler that uses Date for
  absolute time and number for relative time."""
  def __init__(self, initialClock = 0, comparer = defaultSubComparer):
    super(HistoricalScheduler, self).__init__(initialClock, comparer)
    self.clock = initialClock
    self.cmp = comparer

  def add(self, absolute, relative):
    return absolute + relative

  def toDateTimeOffset(self, absolute):
    return datetime.fromtimestamp(absolute)

  def toRelative(self, timeSpan):
    return timeSpan


class ImmediateScheduler(Scheduler):
  """Provides a scheduler that can not schedule"""
  def __init__(self):
    super(ImmediateScheduler, self).__init__(
      defaultNow,
      self._scheduleNow,
      self._scheduleRelative,
      self._scheduleAbsolute
    )

  def _scheduleNow(self, state, action):
    return action(self, state)

  def _scheduleRelative(self, state, dueTime, action):
    if dueTime > 0:
      raise Exception("Scheduler is not allowed to block the current thread")

    return action(this, state)

  def _scheduleAbsolute(self, state, dueTime, action):
    return self.scheduleWithRelativeAndState(state, dueTime - self.now(), action)


class RecursiveScheduledFunction:
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


class PeriodicTimerWithState:
  def __init__(self, interval, function, state):
    self.interval = interval
    self.function = function
    self.args = state
    self.lock = RLock

  def _scheduled(self, run = True):
    if run:
      self.state = self.function(self.state)

    with self.lock:
      self.timer = Timer(self.interval, self._scheduled)

  def _cancel(self):
    with self.lock:
      self.timer.cancel()

  def start(self):
    self._scheduled(False)

    #race condition
    return Disposable.create(self._cancel)


class ScheduledItem:
  """Provides a scheduled cancelable item with state and comparer"""
  def __init__(self, scheduler, state, action, dueTime, comparer = defaultSubComparer):
    self.scheduler = scheduler
    self.state = state
    self.action = action
    self.dueTime = dueTime
    self.comparer = comparer
    self.disposable = SingleAssignmentDisposable()

  def invoke(self):
    self.disposable.disposable(self.invokeCore())

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
