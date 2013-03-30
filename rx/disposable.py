from rx.concurrency import Atomic
from collections import deque

class Disposable:
  """Represents a disposable object"""

  def dispose(self):
    pass

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.dispose()

  @staticmethod
  def create(action):
    return AnonymouseDisposable(action)

  @staticmethod
  def empty():
    return disposableEmpty

disposableEmpty = Disposable()


class Cancelable(Disposable):
  def __init__(self):
    super(Cancelable, self).__init__()
    self._isDisposed = Atomic(False)

  def dispose(self):
    raise NotImplementedError()

  @property
  def isDisposed(self):
    """The isDisposed property."""
    return self._isDisposed.value

  @property
  def lock(self):
    return self._isDisposed.lock


class AnonymouseDisposable(Cancelable):
  def __init__(self, action):
    super(AnonymouseDisposable, self).__init__()
    self.action = action

  def dispose(self):
    if not self._isDisposed.exchange(True):
      self.action()


class BooleanDisposable(Cancelable):
  def __init__(self):
    super(BooleanDisposable, self).__init__()

  def dispose(self):
    self._isDisposed.exchange(True)


class CompositeDisposable(Cancelable):
  """Represents a group of disposable resources that
  are disposed together"""

  def __init__(self, first = None, *rest):
    super(CompositeDisposable, self).__init__()

    if first == None:
      self.disposables = []
    elif isinstance(first, list) or isinstance(first, tuple):
      self.disposables = list(first)
    else:
      self.disposables = [first] + list(rest)

    self.length = len(self.disposables)

  def add(self, item):
    shouldDispose = False

    with self.lock:
      shouldDispose = self.isDisposed

      if not shouldDispose:
        self.disposables.append(item)
        self.length += 1

    if shouldDispose:
      item.dispose()

  def contains(self, item):
    with self.lock:
      return self.disposables.index(item) >= 0

  def remove(self, item):
    shouldDispose = False

    with self.lock:
      if self.isDisposed:
        return False

      index = self.disposables.index(item)

      if index < 0:
        return False

      shouldDispose = True

      self.disposables.remove(item)
      self.length -= 1

    if shouldDispose:
      item.dispose()

    return shouldDispose

  def clear(self):
    disposables = []

    with self.lock:
      disposables = self.disposables
      self.disposables = []
      self.length = 0

    for disposable in disposables:
      disposable.dispose()

  def dispose(self):
    if not self._isDisposed.exchange(True):
      self.clear()


class RefCountDisposable(Cancelable):
  """Represents a disposable resource that only disposes
  its underlying disposable resource when all
  dependent disposable objects have been disposed."""

  class InnerDisposable(Disposable):
    def __init__(self, parent):
      self.parent = Atomic(parent)

    def dispose(self):
      parent = self.parent.exchange(None)

      if parent != None:
        parent.release()


  def __init__(self, disposable):
    super(RefCountDisposable, self).__init__()
    self.disposable = disposable
    self.isPrimaryDisposed = False
    self.count = 0

  def dispose(self):
    disposable = None

    with self.lock:
      if self.isDisposed or self.isPrimaryDisposed:
        return

      self.isPrimaryDisposed = True

      if self.count == 0:
        disposable = self.disposable
        self._isDisposed.value = True

    if disposable != None:
      disposable.dispose()

  def getDisposable(self):
    with self.lock:
      if self.isDisposed:
        return Disposable.empty()
      else:
        return self.InnerDisposable(self)

  def release(self):
    disposable = None

    with self.lock:
      if self.isDisposed:
        return

      self.count -= 1

      if self.isPrimaryDisposed and self.count == 0:
        disposable = self.disposable
        self._isDisposed.value = True

    if disposable != None:
      disposable.dispose()


class SchedulerDisposable(Cancelable):
  """Represents a disposable resource whose disposal invocation
  will be scheduled on the specified Scheduler."""

  def __init__(self, scheduler, disposable):
    super(SchedulerDisposable, self).__init__()
    self.scheduler = scheduler
    self.disposable = disposable

  def dispose(self):
    def fun():
      if not self._isDisposed.exchange(True):
        self.disposable.dispose()

    self.scheduler.schedule(fun)


class SerialDisposable(Cancelable):
  """Represents a disposable resource whose underlying
  disposable resource can be replaced by
  another disposable resource, causing automatic
  disposal of the previous underlying disposable resource.
  Also known as MultipleAssignmentDisposable."""

  def __init__(self):
    super(SerialDisposable, self).__init__()
    self.current = None

  def disposable():
    doc = "The disposable property."
    def fget(self):
      with self.lock:
        if self.isDisposed:
          return Disposable.empty()
        else:
          return self.current
    def fset(self, value):
      old = None
      shouldDispose = False

      with self.lock:
        shouldDispose = self.isDisposed

        if not shouldDispose:
          old = self.current
          self.current = value

      if old != None:
        old.dispose()

      if shouldDispose:
        value.dispose()
    return locals()
  disposable = property(**disposable())

  def dispose(self):
    if not self._isDisposed.exchange(True):
      old = self.current

      self.current = None

      if old != None:
        old.dispose()


class SingleAssignmentDisposable(Cancelable):
  """Represents a disposable resource which only allows
  a single assignment of its underlying disposable resource.
  If an underlying disposable resource has already been set,
  future attempts to set the underlying disposable resource
  will throw an Error."""

  def __init__(self):
    super(SingleAssignmentDisposable, self).__init__()
    self.current = None

  def disposable():
    def fget(self):
      with self.lock:
        if self.isDisposed:
          return Disposable.empty()
        else:
          return self.current
    def fset(self, value):
      old = self.current
      self.current = value

      if old != None: raise Exception("Disposable has already been assigned")

      if self.isDisposed and value != None: value.dispose()
    return locals()

  disposable = property(**disposable())

  def dispose(self):
    if not self._isDisposed.exchange(True):
      if self.current != None:
        self.current.dispose()


class AsyncLock(Cancelable):
  def __init__(self):
    super(AsyncLock, self).__init__()

    self.queue = deque()
    self.isAcquired = False
    self.hasFaulted = False

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

