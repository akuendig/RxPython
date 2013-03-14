from disposable import Disposable, SingleAssignmentDisposable, SerialDisposable, CompositeDisposable
from notification import Notification
from concurrency import Atomic
from internal import noop, defaultError, raiseIsDisposed
from threading import RLock, Semaphore
from queue import Queue

class Observer(object):
  """Represents thi IObserver Interface.
  Has some static helper methods attached"""

  @staticmethod
  def create(onNext=noop, onError=defaultError, onCompleted=noop):
    return AnonymousObserver(onNext, onError, onCompleted)

  @staticmethod
  def synchronize(observer, lock = None):
    if lock == None:
      lock = RLock()

    return SynchronizedObserver(observer, lock)

  @staticmethod
  def fromNotifier(handler):
    return AnonymousObserver(
      lambda x: handler(Notification.createOnNext(x)),
      lambda ex: handler(Notification.createOnError(ex)),
      lambda: handler(Notification.createOnCompleted())
    )

  def toNotifier(self):
    return lambda n: n.accept(self)

  def asObserver(self):
    return AnonymousObserver(self.onNext, self.onError, self.onCompleted)

  def checked(self):
    return CheckedObserver(self)

  def notifyOn(self, scheduler):
    return ScheduledObserver(scheduler, self)

  def onNext(self, value):
    raise NotImplementedError()

  def onError(self, exception):
    raise NotImplementedError()

  def onCompleted(self):
    raise NotImplementedError()


class ObserverBase(Observer):
  """Abstract base class for implementations
  of the IObserver interface.
  This base class enforces the grammar of observers
  where OnError and OnCompleted are terminal messages."""

  def __init__(self):
    self.isStopped = Atomic(False)
    self.lock = self.isStopped.lock

  def onNext(self, value):
    with self.lock:
      if self.isStopped.value:
        return

      self.onNextCore(value)

  def onError(self, exception):
    if not self.isStopped.exchange(True):
      self.onErrorCore(exception)

  def onCompleted(self):
    if not self.isStopped.exchange(True):
      self.onCompletedCore()

  def dispose(self):
    self.isStopped.value = True

  def fail(self, exception):
    if self.isStopped.exchange(True):
      # isStopped was already true
      return False
    else:
      self.onErrorCore(exception)
      return True

  def onNextCore(self, value):
    raise NotImplementedError()

  def onErrorCore(self, exception):
    raise NotImplementedError()

  def onCompletedCore(self):
    raise NotImplementedError()


class AnonymousObserver(ObserverBase):
  def __init__(self, onNext=noop, onError=defaultError, onCompleted=noop):
    super(AnonymousObserver, self).__init__()
    self._onNext = onNext
    self._onError = onError
    self._onCompleted = onCompleted

  def onNextCore(self, value):
    self._onNext(value)

  def onErrorCore(self, exception):
    self._onError(exception)

  def onCompletedCore(self):
    self._onCompleted()

  def makeSafe(self):
    return AutoDetachObserver(self.onNext, self.onError, self.onCompleted)


class AsyncLockObserver(ObserverBase):
  def __init__(self, observer, gate):
    super(AsyncLockObserver, self).__init__()
    self.observer = observer
    self.gate = gate

  def onNextCore(self, value):
    self.gate.wait(lambda: self.observer.onNext(value))

  def onErrorCore(self, exception):
    self.gate.wait(lambda: self.observer.onNext(exception))

  def onCompletedCore(self):
    self.gate.wait(lambda: self.observer.onCompleted())


class AutoDetachObserver(ObserverBase):
  def __init__(self, observer, disposable = None):
    super(AutoDetachObserver, self).__init__()
    self.observer = observer
    self.m = SingleAssignmentDisposable()

    if disposable != None:
      self.m.disposable = disposable

  def onNextCore(self, value):
    noError = False

    try:
      self.observer.onNext(value)
      noError = True
    finally:
      if not noError:
        self.dispose()

  def onErrorCore(self, ex):
    try:
      self.observer.onError(ex)
    finally:
      self.dispose()

  def onCompletedCore(self):
    try:
      self.observer.onCompleted()
    finally:
      self.dispose()

  def disposable():
      doc = "The disposable property."
      def fget(self):
          self.m.disposable
      def fset(self, value):
          self.m.disposable = value
      return locals()
  disposable = property(**disposable())

  def dispose(self):
    with self.lock:
      super(AutoDetachObserver, self).dispose()
      self.m.dispose()


class CheckedObserver(Observer):
  IDLE = 0
  BUSY = 1
  DONE = 2

  def __init__(self, observer):
    super(CheckedObserver, self).__init__()
    self.observer = observer
    self.state = Atomic(CheckedObserver.IDLE)

  def onNext(self, value):
    self.checkAccess()

    try:
      self.observer.onNext(value)
    finally:
      self.state.value = CheckedObserver.IDLE

  def onError(self, exception):
    self.checkAccess()

    try:
      self.observer.onError(exception)
    finally:
      self.state.value = CheckedObserver.DONE

  def onCompleted(self):
    self.checkAccess()

    try:
      self.observer.onCompleted()
    finally:
      self.state.value = CheckedObserver.DONE

  def checkAccess(self):
    old = self.state.compareExchange(CheckedObserver.BUSY, CheckedObserver.IDLE)

    if old == CheckedObserver.BUSY:
      raise Exception("This observer is currently busy")
    elif old == CheckedObserver.DONE:
      raise Exception("This observer already terminated")


class ScheduledObserver(ObserverBase):
  STOPPED = 0
  RUNNING = 1
  PENDING = 2
  FAULTED = 9

  def __init__(self, scheduler, observer):
    super(ScheduledObserver, self).__init__()
    self.scheduler = scheduler
    self.observer = observer
    self.state = Atomic(ScheduledObserver.STOPPED, self.lock)
    self.disposable = SerialDisposable()

    self.failed = False
    self.exception = None
    self.completed = False

    self.queue = Queue()
    self.dispatcherJob = None
    self.dispatcherEvent = Semaphore(0)

  def ensureDispatcher(self):
    if self.dispatcherJob != None:
      return

    with self.lock:
      if self.dispatcherJob == None:
        self.dispatcherJob = self.scheduler.scheduleLongRunning(self.dispatch)
        self.disposable.disposable = CompositeDisposable(
          self.dispatcherJob,
          Disposable.create(lambda: self.dispatcherEvent.release())
        )

  def dispatch(self, cancel):
    while True:
      self.dispatcherEvent.acquire()

      if cancel.isDisposed:
        return

      while True:
        next = self.queue.get_nowait()

        try:
          self.observer.onNext(next)
        except Exception as e:
          while self.queue.get_nowait() != None:
            pass

          raise e

        self.dispatcherEvent.acquire()

        if cancel.isDisposed:
          return

      if self.failed:
        self.observer.onError(self.exception)
        self.dispose()

        return

      if self.completed:
        self.observer.onCompleted()
        self.dispose()

        return

  def ensureActive(self, n = 1):
    try:
      if n > 0:
        self.ensureDispatcher()

        while n > 0:
          self.dispatcherEvent.release()
          n -= 1
    except NotImplementedError:
      self.ensureActiveSlow()

  def ensureActiveSlow(self):
    isOwner = False

    while True:
      old = self.state.compareExchange(
        ScheduledObserver.RUNNING,
        ScheduledObserver.STOPPED
      )

      if old == ScheduledObserver.STOPPED:
        isOwner = True
        break
      elif old == ScheduledObserver.FAULTED:
        return
      elif (
          (old == ScheduledObserver.PENDING or old == ScheduledObserver.RUNNING) and
          self._casState(ScheduledObserver.PENDING, ScheduledObserver.RUNNING) == ScheduledObserver.RUNNING
        ):
        break

    if isOwner:
      self.disposable = self.scheduler.scheduleRecursiveWithState(None, self.run)

  def run(self, state, continuation):
    next = self.queue.get_nowait()

    while True:
      next = self.queue.get_nowait()

      if next != None:
        break

      if self.failed:
        # wait until the queue is drained
        if not self.queue.empty():
          continue

        self.state.value = ScheduledObserver.STOPPED

        self.observer.onError(self.exception)
        self.dispose()

        return

      if self.completed:
        # wait until the queue is drained
        if not self.queue.empty():
          continue

        self.state.value = ScheduledObserver.STOPPED

        self.observer.onCompleted()
        self.dispose()

        return

      old = self.state.compareExchange(
        ScheduledObserver.STOPPED,
        ScheduledObserver.RUNNING
      )

      if old == ScheduledObserver.RUNNING or old == ScheduledObserver.FAULTED:
        return

      # assert(old == ScheduledObserver.PENDING)

      self.state.value = ScheduledObserver.RUNNING

    # we found an item, so next != None
    self.state.value = ScheduledObserver.RUNNING

    try:
      self.observer.onNext(next)
    except Exception as e:
      self.state.value = ScheduledObserver.FAULTED

      while self.queue.get_nowait() != None:
        pass

      raise e

    continuation(state)

  def onNextCore(self, value):
    self.queue.put(value)

  def onErrorCore(self, exception):
    self.exception = exception
    self.failed = True

  def onCompletedCore(self):
    self.completed = True

  def dispose(self):
    super(AutoDetachObserver, self).dispose()
    self.disposable.dispose()


class ObserveOnObserver(ScheduledObserver):
  def __init__(self, scheduler, observer, cancel):
    super(ObserveOnObserver, self).__init__(scheduler, observer)
    self.cancel = Atomic(cancel, self.lock)

  def onNextCore(self, value):
    super(ObserveOnObserver, self).onNextCore(value)
    self.ensureActive()

  def onErrorCore(self, exception):
    super(ObserveOnObserver, self).onErrorCore(exception)
    self.ensureActive()

  def onCompletedCore(self):
    super(ObserveOnObserver, self).onCompletedCore()
    self.ensureActive()

  def dispose(self):
    super(ObserveOnObserver, self).dispose()

    old = self.cancel.exchange(None)

    if old != None:
      old.dispose()


class SynchronizedObserver(ObserverBase):
  def __init__(self, observer, lock):
    super(SynchronizedObserver, self).__init__()
    self.observer = observer
    self.outerLock = lock

  def onNextCore(self, value):
    with self.outerLock:
      self.observer.onNext(value)

  def onErrorCore(self, exception):
    with self.outerLock:
      self.observer.onError(exception)

  def onCompletedCore(self):
    with self.outerLock:
      self.observer.onCompleted()


noopObserver = Observer.create(noop, noop, noop)
Observer.noop = noopObserver

doneObserver = Observer.create(noop, noop, noop)
doneObserver.exception = None
Observer.done = doneObserver

disposedObserver = Observer.create(raiseIsDisposed, raiseIsDisposed, raiseIsDisposed)
Observer.disposed = disposedObserver
