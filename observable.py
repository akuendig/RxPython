from .observer import Observer

class Observable(object):
  def __init__(self, subscribe):
    super(Observable, self).__init__()
    self._subscribe = subscribe

  def subscribe(self, observerOrOnNext=None, onError=None, onComplete=None):
    if observerOrOnNext == None or hasattr(observerOrOnNext, '__call__'):
      self._subscribe(Observer.create(observerOrOnNext, onError, onComplete))
    else:
      self._subscribe(observerOrOnNext)

  @classmethod
  def create(cls, subscribe):
    return Observable(subscribe)
