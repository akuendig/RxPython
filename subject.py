import sys
from .observable import Observable
from .observer import Observer, ScheduledObserver
from .disposable import Disposable
from .scheduler import currentThreadScheduler
from .internal import errorIfDisposed, Struct

class Subject(Observable, Observer):
  def _subscribe(self, observer):
    errorIfDisposed(self)

    if not self.isStopped:
      self.observers.append(observer)
      return Disposable.create(lambda: self.observers.remove(observer))

    if self.exception != None:
      observer.onError(self.exception)
      return Disposable.empty()

  def __init__(self):
    super(Subject, self).__init__(self._subscribe)
    self.isDisposable = False
    self.isStopped = False
    self.observers = []

  def onCompleted(self):
    errorIfDisposed(self)

    if not self.isStopped:
      self.isStopped = True

      for observer in list(self.observers):
        observer.onCompleted()

      self.observers = []

  def onError(self, exception):
    errorIfDisposed(self)

    if not self.isStopped:
      self.isStopped = True
      self.exception = exception

      for observer in list(self.observers):
        observer.onError(exception)

      self.observers = []

  def onNext(self, value):
    errorIfDisposed(self)

    if not self.isStopped:
      for observer in list(self.observers):
        observer.onNext(value)

  def dispose(self):
    self.isDisposed = True
    self.observers = []

  @staticmethod
  def create(observer, observable):
    return AnonymousSubject(observer, observable)


class AnonymousSubject(Observable):
  def _subscribe(self, observer):
    return self.observable.subscript(observer)

  def __init__(self, observer, observable):
    super(AnonymousSubject, self).__init__(self._subscribe)
    self.observer = observer
    self.observable = observable

  def onCompleted(self):
    self.observer.onCompleted()

  def onError(self, exception):
    self.observer.onError(exception)

  def onNect(self, value):
    self.observer.onNext(value)


class AsyncSubject(Observable, Observer):
  def _subscribe(self, observer):
    errorIfDisposed(self)

    if not self.isStopped:
      self.observers.append(observer)
      return Disposable.create(lambda: self.observers.remove(observer))

    if self.exception != None:
      observer.onError(self.exception)
    elif self.hasValue:
      observer.onNext(self.value)
      observer.onCompleted()
    else:
      observer.onCompleted()

    return Disposable.empty()

  def __init__(self):
    super(AsyncSubject, self).__init__(self._subscribe)
    self.isDisposed = False
    self.isStopped = False
    self.value = None
    self.hasValue = False
    self.observers = []
    self.exception = None

  def onCompleted(self):
    errorIfDisposed(self)

    if self.isStopped:
      return

    self.isStopped = True

    if self.hasValue:
      for observer in list(self.observers):
        observer.onNext(self.value)
        observer.onCompleted()
    else:
      for observer in list(self.observers):
        observer.onCompleted()

    self.observers = []

  def onError(self, exception):
    errorIfDisposed(self)

    if self.isStopped:
      return

    self.isStopped = True
    self.exception = exception

    for observer in list(self.observers):
      observer.onError(exception)

    self.observers = []

  def onNext(self, value):
    errorIfDisposed(self)

    if self.isStopped:
      return

    for observer in list(self.observers):
      observer.onNext(value)

  def dispose(self):
    self.isDisposed = True
    self.observers = []
    self.exception = None
    self.value = None


class BehaviorSubject(Observable, Observer):
  def _subscribe(self, observer):
    errorIfDisposed(self)

    if not self.isStopped:
      self.observers.append(observer)
      observer.onNext(self.value)
      return Disposable.create(lambda: self.observables.remove(observer))

    if self.exception != None:
      observer.onError(self.exception)
    else:
      observer.onCompleted()

    return Disposable.empty()

  def __init__(self, value):
    super(BehaviorSubject, self).__init__(self._subscribe)

    self.value = value
    self.observers = []
    self.isDisposed = False
    self.isStopped = False
    self.exception = None

  def onCompleted(self):
    errorIfDisposed(self)

    if self.isStopped:
      return

    self.isStopped = True

    for observer in list(self.observers):
      observer.onCompleted()

    self.observers = []

  def onError(self, exception):
    errorIfDisposed(self)

    if self.isStopped:
      return

    self.isStopped = True
    self.exception = exception

    for observer in list(self.observers):
      observer.onError(exception)

    self.observers = []

  def onNext(self, value):
    errorIfDisposed(self)

    if self.isStopped:
      return

    self.value = value

    for observer in list(self.observers):
      observer.onNext(value)

  def dispose(self):
    self.isDisposed = True
    self.observers = []
    self.value = None
    self.exception = None


class ReplaySubject(Observable, Observer):

  class RemovableDisposable(Disposable):
    def __init__(self, subject, observer):
      super(self.__class__, self).__init__()
      self.subject = subject
      self.observer = observer

    def dispose(self):
      self.observer.dispose()

      if not self.subject.isDisposed:
        self.subject.observers.remove(self.observer)

  def _subscribe(self, observer):
    so = ScheduledObserver(self.scheduler, observer)
    subscription = self.__class__(self, so)

    errorIfDisposed(self)

    self._trim(self.scheduler.now())
    self.observers.append(so)

    n = len(self.q)

    for node in self.q:
      so.onNext(node.value)

    if self.hasError:
      n += 1
      so.onError(self.exception)
    elif self.isStopped:
      n += 1
      so.onCompleted()

    so.ensureActive(n)

    return subscription

  def __init__(self, bufferSize = sys.maxsize, window = sys.maxsize, scheduler = currentThreadScheduler):
    self.bufferSize = bufferSize
    self.window = window
    self.scheduler = scheduler
    self.q = []
    self.observers = []
    self.isStopped = False
    self.isDisposed = False
    self.hasError = False
    self.exception = None
    super(ReplaySubject, self).__init__(self._subscribe)

  def _trim(self, now):
    self.q = self.q[-self.bufferSize:]
    self.q = [node for node in self.q if self.window >= (now - node.interval)]

  def onNext(self, value):
    errorIfDisposed(self)

    if self.isStopped:
      return

    now = self.scheduler.now()

    self.q.append(Struct(interval = now, value = value))
    self._trim(now)

    for observer in list(self.observers):
      observer.onNext(value)
      observer.ensureActive()

  def onError(self, exception):
    errorIfDisposed(self)

    if self.isStopped:
      return

    self.isStopped = True
    self.exception = exception
    self.hasError = True

    now = self.scheduler.now()

    self._trim(now)

    for observer in list(self.observers):
      observer.onError(exception)
      observer.ensureActive()

    self.observers = []

  def onCompleted(self):
    errorIfDisposed(self)

    if self.isStopped:
      return

    self.isStopped = True

    now = self.scheduler.now()

    self._trim(now)

    for observer in list(self.observers):
      observer.onCompleted()
      observer.ensureActive()

    self.observers = []

  def dispose(self):
    self.isDisposed = True
    self.observers = []

