from .disposable import Disposable, CompositeDisposable, SingleAssignmentDisposable
from .functional import bind
from .internal import defaultSubComparer
from collections import deque
from threading import RLock, Timer

class Atomic:
  def __init__(self, value=None, lock=RLock()):
    self.lock = lock
    self._value = value

  def value():
      doc = "The value property."
      def fget(self):
          return self._value
      def fset(self, value):
          self.exchange(value)
      return locals()
  value = property(**value())

  def exchange(self, value):
    with self.lock:
      old = self.value
      self.value = value
      return old

  def compareExchange(self, value, expected):
    with self.lock:
      old = self.value

      if old == expected:
        self.value = value

      return old

  def inc(self, by=1):
    with self.lock:
      self.value += by
      return self.value

  def dec(self, by=1):
    with self.lock:
      self.value -= by
      return self.value


class AsyncLock(Disposable):
  def __init__(self):
    super(AsyncLock, self).__init__()

    self.queue = deque()
    self.isAcquired = False
    self.hasFaulted = False
    self.lock = RLock()

  def wait(self, action):
    isOwner = False

    with self.lock:
      if not self.hasFaulted:
        isOwner = not self.isAcquired
        self.queue.appendleft(action)
        self.isAcquired  = True

    if isOwner:
      while True:
        if len(self.queue) == 0:
          self.isAcquired = False
          break

        work = self.queue.pop()

        try:
          work()
        except Exception as e:
          self.dispose()
          raise e

  def dispose(self):
    with self.lock:
      self.queue.clear()
      self.hasFaulted = True


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