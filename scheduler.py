from .disposable import Disposable, CompositeDisposable
from .functional import bind
from .internal import defaultNow
from threading import Timer

class PeriodicTimerWithState:
  def __init__(self, interval, function, state):
    self.interval = interval
    self.function = function
    self.args = state

  def _scheduled(self, run = True):
    if run:
      self.state = self.function(self.state)

    #race condition
    self.timer = Timer(self.interval, self._scheduled)

  def start(self):
    self._scheduled(False)

    #race condition
    return Disposable.create(lambda: self.timer.cancel())


class RecursiveScheduledFunction:
  def __init__(self, action, scheduler, method = None):
    self.action = action
    self.schedule = scheduler if method == None else scheduler[method]
    self.group = CompositeDisposable()

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

    # Assuming no concurrent access otherwise we would have
    # a race for self.group, self.isAdded and self.isDone
    if not self.isDone:
      self.group.add(self.cancel)
      self.isAdded = True

  def schedulerCallback(self, scheduler, state):
    if self.isAdded:
      self.group.remove(self.cancel)
    else:
      self.isDone = True

    self.run(state)

    return Disposable.empty()


class Scheduler(object):
  """Provides a set of static properties to access commonly
  used Schedulers."""

  def __init__(self, now, schedule, scheduleRelative, scheduleAbsolute):
    self.now = now
    self._schedule = schedule
    self._scheduleRelative = scheduleRelative
    self._scheduleAbsolute = scheduleAbsolute

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
  def invokeAction(scheduler, action):
    action()
    return Disposable.empty()

  def catchException(self, handler):
    return CatchScheduler(self, handler)

  def schedulePeriodic(self, period, action):
    return self.schedulerPeriodicWithState(None, period, lambda s: action())

  def schedulePeriodicWithState(self, state, period, action):
    timer = PeriodicTimerWithState(period, action, state)
    return timer.start()

  #Suspiciouse
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

  def scheduleRecursive(self, action):
    return self.scheduleRecursiveWithState(
      action,
      lambda _action, _self: _action(lambda: _self(_action)
    ))

  def scheduleRecursiveWithState(self, state, action):
    return self.scheduleWithState((state, action), Scheduler.invokeRecImmediate)

  def scheduleRecursiveWithRelative(self, dueTime, action):
    return self.scheduleRecursiveWithRelativeAndState(
      action,
      dueTime,
      lambda _action, _self: _action(lambda dt: _self(_action, dt)
    ))

  def scheduleRecursiveWithRelativeAndState(self, state, dueTime, action):
    return self._scheduleRelative(
      (state, action),
      dueTime,
      lambda s, p: Scheduler.invokeRecDate(s, p, 'scheduleWithRelativeAndState'
    ))

  def scheduleRecursiveWithAbsolute(self, dueTime, action):
    return self.scheduleRecursiveWithAbsoluteAndState(
      action,
      lambda _action, _self: _action(lambda: _self(_action)
    ))

  def scheduleRecursiveWithAbsoluteAndState(self, state, dueTime, action):
    return self._scheduleRelative(
      (state, action),
      dueTime,
      lambda s, p: Scheduler.invokeRecDate(s, p, 'scheduleWithAbsoluteAndState'
    ))

  @staticmethod
  def now():
    return defaultNow()

  @staticmethod
  def normalize(timeSpan):
    if timeSpan < 0:
      return 0
    else:
      return timeSpan

