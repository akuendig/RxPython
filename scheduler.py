from .disposable import Disposable, CompositeDisposable

class RecursiveScheduledFunction:
  def __init__(self, action, scheduler):
    self.action = action
    self.scheduler = scheduler
    self.group = CompositeDisposable()

  def run(self, state):
    self.action(state, self.actionCallback)

  def actionCallback(self, newState):
    self.isDone = False
    self.isAdded = False

    self.cancel = self.scheduler.scheduleWithState(newState, self.schedulerCallback)

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

  def invokeRecImmediate(scheduler, pair):
    state = pair[0]
    action = pair[1]

    scheduled = RecursiveScheduledFunction(action, scheduler)
    scheduled.run(state)

    return scheduled.group
