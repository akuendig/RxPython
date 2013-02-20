from .internal import noop

class Disposable:
  """Represents a disposable object"""
  def __init__(self, action = None):
    self.action = action
    self.isDisposed = False

  def dispose(self):
    if self.isDisposed:
      return

    self.action()
    self.isDisposed = True

  @staticmethod
  def create(action):
    return Disposable(action)

  @staticmethod
  def empty():
    return Disposable(noop)


class SingleAssignmentDisposable(Disposable):
  """Represents a disposable resource which only allows
  a single assignment of its underlying disposable resource.
  If an underlying disposable resource has already been set,
  future attempts to set the underlying disposable resource
  will throw an Error."""

  def __init__(self):
    super(SingleAssignmentDisposable, self).__init__()

    self.isDisposed = False
    self.current = None

  def disposable():
    def fget(self):
      return self.current
    def fset(self, value):
      if self.current != None: raise Exception("Disposable has already been assigned")
      if not self.isDisposed: self.current = value
      if self.isDisposed and value != None: value.dispose()
    return locals()

  disposable = property(**disposable())

  def dispose(self):
    if self.isDisposed: return

    self.isDisposed = True

    if self.current != None:
      self.current.dispose()

    self.current = None


class RefCountDisposable(Disposable):
  """Represents a disposable resource that only disposes
  its underlying disposable resource when all
  <see cref="GetDisposable">dependent disposable objects
  </see> have been disposed."""

  class InnerDisposable(Disposable):
    def __init__(self, disposable):
      self.disposable = disposable
      self.disposable.count += 1
      self.isInnerDisposed = False

    def dispose(self):
      if self.disposable.isInnerDisposed or self.isInnerDisposed:
        return

      self.isInnerDisposed = True
      self.disposable.count -= 1

      if self.disposable.count == 0 and self.disposable.isPrimaryDisposed:
        self.disposable.isDisposed = True
        self.disposable.underlyingDisposable.dispose()


  def __init__(self, disposable):
    super(RefCountDisposable, self).__init__()
    self.underlyingDisposable = disposable
    self.isDisposed = False
    self.isPrimaryDisposed = False
    self.count = 0

  def dispose(self):
    if self.isDisposed or self.isPrimaryDisposed:
      return

    self.isPrimaryDisposed = True

    if self.count == 0:
      self.isDisposed = True
      self.underlyingDisposable.dispose()

  def getDisposable(self):
    if self.isDisposed:
      return Disposable.empty
    else:
      return self.InnerDisposable(self)


class SerialDisposble(Disposable):
  """Represents a disposable resource whose underlying
  disposable resource can be replaced by
  another disposable resource, causing automatic
  disposal of the previous underlying disposable resource."""

  def __init__(self):
    super(SerialDisposble, self).__init__()
    self.isDisposed = False
    self.current = None

  def disposable():
    doc = "The disposable property."
    def fget(self):
      return self.current
    def fset(self, value):
      if not self.isDisposed:
        old = self.current
        self.current = value

        if old != None:
          old.dispose()

      if self.isDisposed and value != None:
        value.dispose()
    return locals()
  disposable = property(**disposable())

  def dispose(self):
    self.disposable = None
    self.isDisposed = True


class CompositDisposable(Disposable):
  """Represents a group of disposable resources that
  are disposed together"""

  def __init__(self, first = None, *rest):
    super(CompositDisposable, self).__init__()

    if first != None and (isinstance(first, list) or isinstance(first, tuple)):
      self.disposables = list(first)
    else:
      self.disposables = [first] + list(rest)

    self.isDisposed = False
    self.length = len(self.disposables)

  def add(self, item):
    if self.isDisposed:
      item.dispose()
    else:
      self.disposables.append(item)
      self.length += 1

  def remove(self, item):
    if self.isDisposed:
      return False

    index = self.disposables.index(item)

    if index < 0:
      return False

    self.disposables.remove(item)
    self.length -= 1

    item.dispose()
    return True

  def dispose(self):
    if self.isDisposed:
      return

    self.isDisposed = True

    disposables = self.disposables

    self.disposables = []
    self.length = 0

    for disposable in disposables:
      disposable.dispose()

  def contains(self, item):
    return self.disposables.index(item) >= 0


class SchedulerDisposable(Disposable):
  def __init__(self, scheduler, disposable):
    super(SchedulerDisposable, self).__init__()
    self.scheduler = scheduler
    self.disposable = disposable
    self.isDisposed = False

  def dispose(self):
    def fun():
      if not self.isDisposed:
        self.isDisposed = True
        self.disposable.dispose()

    self.scheduler.schedule(fun)




