from .functional import *
from .disposable import *
from .internal import *

class Observer(object):
  @staticMethod
  def create(onNext=noop, onError=defaultError, onComplete=noop):
    return AnonymousObserver(onNext, onError, onComplete)

class AnonymousObserver(Observer):
  def __init__(self, onNext, onError, onComplete):
    super(AnonymousObserver, self).__init__()
    self.onNext = onNext
    self.onError = onError
    self.onComplete = onComplete

class AutoDetachObserver(Observer):
  def __init__(self, observer):
    super(AutoDetachObserver, self).__init__()
    self.observer = observer
    self.m = SingleAssignmentDisposable()

  def next(self, value):
    noError = False

    try:
      self.observer.onNext(value)
      noError = true
    finally:
      if not noError:
        self.dispose()

  def error(self, ex):
    try:
      self.observer.onError(ex)
    finally:
      self.dispose()

  def completed(self):
    try:
      self.observer.onCompleted()
    finally:
      self.dispose()

  def disposable(self, value):
    return self.m.disposable(value)

  def dispose(self):
    super(AutoDetachObserver, self).dispose()
    self.m.dispose()
