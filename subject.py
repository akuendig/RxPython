from .observable import Observable
from .observer import Observer
from .disposable import Disposable
from .internal import errorIfDisposed

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

