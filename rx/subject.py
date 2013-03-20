from rx.concurrency import Atomic
from rx.disposable import Disposable
from rx.internal import errorIfDisposed, Struct
from rx.observable import Observable
from rx.observer import DisposedObserver, DoneObserver, NoopObserver, ListObserver, Observer, ScheduledObserver
from rx.scheduler import currentThreadScheduler
import sys
from threading import RLock

class Subject(Observable, Observer):
  def __init__(self):
    super(Subject, self).__init__()
    self.isDisposed = False
    self.isStopped = False
    self.exception = None
    self.observer = Atomic(NoopObserver.instance)

  def onCompleted(self):
    old = None
    new = DoneObserver.completed

    while True:
      old = self.observer.value

      if old is DoneObserver.completed or isinstance(old, DoneObserver):
        break

      current = self.observer.compareExchange(new, old)

      if old is current:
        break

    old.onCompleted()

  def onError(self, exception):
    old = None
    new = DoneObserver(exception)

    while True:
      old = self.observer.value

      if old is DoneObserver.completed or isinstance(old, DoneObserver):
        break

      current = self.observer.compareExchange(new, old)

      if old is current:
        break

    old.onError(exception)

  def onNext(self, value):
    self.observer.value.onNext(value)

  class Subscription(Disposable):
    def __init__(self, subject, observer):
      self.subject = subject
      self.observer = Atomic(observer)

    def dispose(self):
      old = self.observer.exchange(None)

      if old != None:
        self.subject.unsubscribe(old)
        self.subject = None

  def subscribeCore(self, observer):
    old = None
    new = None

    while True:
      old = self.observer.value

      if old is DisposedObserver.instance:
        raise Exception("Object has been disposed")

      if old is DoneObserver.completed:
        observer.onCompleted()
        return Disposable.empty()

      if isinstance(old, DoneObserver):
        observer.onError(old.exception)
        return Disposable.empty()

      if old is NoopObserver.instance:
        new = observer
      else:
        if isinstance(old, ListObserver):
          new = old.add(observer)
        else:
          new = ListObserver((old, observer))

      current = self.observer.compareExchange(new, old)

      if old is current:
        break

    return self.Subscription(self, observer)

  def unsubscribe(self, observer):
    old = None
    new = None

    while True:
      old = self.observer.value

      if old is DisposedObserver.instance or isinstance(old, DoneObserver):
        return

      if isinstance(old, ListObserver):
        new = old.remove(observer)
      elif observer is not old:
        return
      else:
        new = NoopObserver.instance

      current = self.observer.compareExchange(new, old)

      if old is current:
        return

  def dispose(self):
    self.observer.exchange(NoopObserver.instance)

  @staticmethod
  def create(observer, observable):
    return AnonymousSubject(observer, observable)

  @staticmethod
  def synchronize(subject, scheduler=None):
    if scheduler == None:
      return AnonymousSubject(Observer.synchronize(subject), subject)
    else:
      return AnonymousSubject(Observer.synchronize(subject), subject.observeOn(scheduler))


class AnonymousSubject(Observable, Observer):
  """Represents a proxy subject. All Observer calls go to the observer
  passed as parameter and all subscribe calls go to the observable passed
  as parameter"""

  def __init__(self, observer, observable):
    super(AnonymousSubject, self).__init__()
    self.observer = observer
    self.observable = observable

  def onCompleted(self):
    self.observer.onCompleted()

  def onError(self, exception):
    self.observer.onError(exception)

  def onNext(self, value):
    self.observer.onNext(value)

  def subscribeCore(self, observer):
    return self.observable.subscribe(observer)


class AsyncSubject(Observable, Observer):
  def __init__(self):
    super(AsyncSubject, self).__init__()
    self.isDisposed = False
    self.isStopped = False
    self.value = None
    self.hasValue = False
    self.observers = []
    self.exception = None
    self.gate = RLock()

  @property
  def hasObservers(self):
    os = self.observers
    return os != None and len(os) > 0

  def onCompleted(self):
    os = []
    v = None
    hv = False

    with self.gate:
      errorIfDisposed(self)

      if not self.isStopped:
        os = list(self.observers)

        self.isStopped = True
        self.observers = []
        v = self.value
        hv = self.hasValue

    if hv:
      for observer in os:
        observer.onNext(v)
        observer.onCompleted()
    else:
      for observer in os:
        observer.onCompleted()

  def onError(self, exception):
    os = []

    with self.gate:
      errorIfDisposed(self)

      if not self.isStopped:
        os = list(self.observers)

        self.isStopped = True
        self.observers = []
        self.exception = exception

    for observer in os:
      observer.onError(exception)

  def onNext(self, value):
    with self.gate:
      errorIfDisposed(self)

      if not self.isStopped:
        self.value = value
        self.hasValue = True

  def subscribeCore(self, observer):
    ex = None
    v = None
    hv = False

    with self.gate:
      errorIfDisposed(self)

      if not self.isStopped:
        self.observers.append(observer)
        return Subject.Subscription(self, observer)

      ex = self.exception
      hv = self.hasValue
      v = self.value

    if ex != None:
      observer.onError(ex)
    elif hv:
      observer.onNext(v)
      observer.onCompleted()
    else:
      observer.onCompleted()

    return Disposable.empty()

  def unsubscribe(self, observer):
    with self.gate:
      if observer in self.observer:
        self.observers.remove(observer)

  def dispose(self):
    with self.gate:
      self.isDisposed = True
      self.observers = []
      self.exception = None
      self.value = None


class BehaviorSubject(Observable, Observer):
  def __init__(self, value):
    super(BehaviorSubject, self).__init__()

    self.value = value
    self.observers = []
    self.isDisposed = False
    self.isStopped = False
    self.exception = None
    self.gate = RLock()

  @property
  def hasObservers(self):
    os = self.observers
    return os != None and len(os) > 0

  def onCompleted(self):
    os = []
    with self.gate:
      errorIfDisposed(self)

      if not self.isStopped:
        os = list(self.observers)

        self.isStopped = True
        self.observers = []

    for observer in os:
      observer.onCompleted()

  def onError(self, exception):
    os = []

    with self.gate:
      errorIfDisposed(self)

      if not self.isStopped:
        os = list(self.observers)

        self.isStopped = True
        self.observers = []
        self.exception = exception

    for observer in os:
      observer.onError(exception)

  def onNext(self, value):
    os = []

    with self.gate:
      errorIfDisposed(self)

      if not self.isStopped:
        os = list(self.observers)

        self.value = value

    for observer in os:
      observer.onNext(value)

  def subscribeCore(self, observer):
    ex = None

    with self.gate:
      errorIfDisposed(self)

      if not self.isStopped:
        self.observers.append(observer)
        observer.onNext(self.value)
        return Subject.Subscription(self, observer)

      ex = self.exception

    if ex != None:
      observer.onError(ex)
    else:
      observer.onCompleted()

    return Disposable.empty()

  def unsubscribe(self, observer):
    with self.gate:
      if observer in self.observers:
        self.observers.remove(observer)

  def dispose(self):
    with self.gate:
      self.isDisposed = True
      self.observers = []
      self.value = None
      self.exception = None


class ReplaySubject(Observable, Observer):
  def __init__(self, bufferSize = sys.maxsize, window = sys.maxsize, scheduler = currentThreadScheduler):
    super(ReplaySubject, self).__init__()
    self.bufferSize = bufferSize
    self.window = window
    self.scheduler = scheduler
    self.q = []
    self.observers = []
    self.isStopped = False
    self.isDisposed = False
    self.hasError = False
    self.exception = None
    self.gate = RLock()

  @property
  def hasObservers(self):
    os = self.observers
    return os != None and len(os) > 0

  def _trim(self, now):
    self.q = self.q[-self.bufferSize:]
    self.q = [node for node in self.q if self.window >= (now - node.interval)]

  def onCompleted(self):
    os = []

    with self.gate:
      errorIfDisposed(self)

      if not self.isStopped:
        os = list(self.observers)
        now = self.scheduler.now()

        self.isStopped = True
        self.observers = []

        self._trim(now)

        for observer in os:
          observer.onCompleted()

    for observer in os:
      observer.ensureActive()

  def onError(self, exception):
    os = []

    with self.gate:
      errorIfDisposed(self)

      if not self.isStopped:
        os = list(self.observers)
        now = self.scheduler.now()

        self.isStopped = True
        self.observers = []
        self.exception = exception

        self._trim(now)

        for observer in os:
          observer.onError(exception)

    for observer in os:
      observer.ensureActive()

  def onNext(self, value):
    os = []

    with self.gate:
      errorIfDisposed(self)

      if not self.isStopped:
        os = list(self.observers)
        now = self.scheduler.now()

        self.q.append(Struct(interval = now, value = value))

        for observer in os:
          observer.onNext(value)

    for observer in os:
      observer.ensureActive()

  class Subscription(Disposable):
    def __init__(self, subject, observer):
      self.subject = subject
      self.observer = Atomic(observer)

    def dispose(self):
      old = self.observer.exchange(None)

      if old != None:
        old.dispose()
        self.subject.unsubscribe(old)
        self.subject = None

  def subscribeCore(self, observer):
    so = ScheduledObserver(self.scheduler, observer)
    n = 0
    subscription = self.Subscription(self, so)

    with self.gate:
      errorIfDisposed(self)

      self._trim(self.scheduler.now())
      self.observers.append(so)

      n = len(self.q)

      for item in self.q:
        so.onNext(item.value)

      if self.exception != None:
        n += 1
        so.onError(self.exception)
      elif self.isStopped:
        n += 1
        so.onCompleted()

    so.ensureActive(n)

    return subscription

  def unsubscribe(self, observer):
    with self.gate:
      if observer in self.observers:
        self.observers.remove(observer)

  def dispose(self):
    with self.gate:
      self.isDisposed = True
      self.observers = []

