from .observer import Observer, AutoDetachObserver
from .scheduler import currentThreadScheduler
from .disposable import Disposable

class Observable(object):
  def subscribe(self, observerOrOnNext=None, onError=None, onComplete=None):
    observer = observerOrOnNext

    if observerOrOnNext == None or hasattr(observerOrOnNext, '__call__'):
      observer = Observer.create(observerOrOnNext, onError, onComplete)

    autoDetachObserver = AutoDetachObserver(observer)

    if currentThreadScheduler.isScheduleRequired():
      currentThreadScheduler.scheduleWithState(autoDetachObserver, self.scheduledSubscribe)
    else:
      try:
        autoDetachObserver.disposable(self.subscribeCore(autoDetachObserver))
      except Exception as e:
        if not autoDetachObserver.fail(e):
          raise e

    return autoDetachObserver

  def scheduledSubscribe(self, scheduler, autoDetachObserver):
    try:
      autoDetachObserver.disposable(self.subscribeCore(autoDetachObserver))
    except Exception as e:
      if not autoDetachObserver.fail(e):
        raise e

    return Disposable.empty()

  def subscribeCore(self, observer):
    raise NotImplementedError()

  @classmethod
  def create(cls, subscribe):
    return Observable(subscribe)


class AnonymousObservable(Observable):
  def __init__(self, subscribe):
    super(AnonymousObservable, self).__init__()
    self._subscribe = subscribe

  def subscribeCore(self, observer):
    d = self._subscribe(observer)

    if d == None:
      return Disposable.empty()
    else:
      return d

