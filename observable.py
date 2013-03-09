from observer import Observer, AutoDetachObserver
from scheduler import Scheduler
from disposable import Disposable, CompositeDisposable, SingleAssignmentDisposable

class Observable(object):
  """Provides all extension methods to Observable"""

  @staticmethod
  def create(subscribe):
    return AnonymousObservable(subscribe)

  def subscribe(self, observerOrOnNext=None, onError=None, onComplete=None):
    observer = observerOrOnNext

    if observerOrOnNext == None or hasattr(observerOrOnNext, '__call__'):
      observer = Observer.create(observerOrOnNext, onError, onComplete)

    return self.subscribeCore(observer)

  def subscribeCore(self, observer):
    raise NotImplementedError()

  def subscribeSafe(self, observer):
    if isinstance(self, ObservableBase):
      return self.subscribeCore(observer)
    elif isinstance(self, Producer):
      return self.subscribeRaw(observer, False)

    d = Disposable.empty()

    try:
      d = self.subscribeCore(observer)
    except Exception as e:
      observer.onError(e)

    return d


class ObservableBase(Observable):

  def subscribe(self, observerOrOnNext=None, onError=None, onComplete=None):
    observer = observerOrOnNext

    if observerOrOnNext == None or hasattr(observerOrOnNext, '__call__'):
      observer = Observer.create(observerOrOnNext, onError, onComplete)

    autoDetachObserver = AutoDetachObserver(observer)

    if Scheduler.currentThread.isScheduleRequired():
      Scheduler.currentThread.scheduleWithState(autoDetachObserver, self.scheduledSubscribe)
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


class AnonymousObservable(ObservableBase):
  def __init__(self, subscribe):
    super(AnonymousObservable, self).__init__()
    self._subscribe = subscribe

  def subscribeCore(self, observer):
    d = self._subscribe(observer)

    if d == None:
      return Disposable.empty()
    else:
      return d


class GroupedObservable(ObservableBase):
  def __init__(self, key, subject, refCount=None):
    super(GroupedObservable, self).__init__()
    self.key = key
    self.subject = subject
    self.refCount = refCount

  def subscribeCore(self, observer):
    if self.refCount == None:
      # [OK] Use of unsafe Subscribe: called on a known subject implementation.
      return self.subject.subscribe(observer)
    else:
      # [OK] Use of unsafe Subscribe: called on a known subject implementation.
      release = self.refCount.getDisposable()
      subscription = self.subject.subscribe(observer)
      return CompositeDisposable(release, subscription)

class Producer(Observable):
  """Base class for implementation of query operators, providing
  performance benefits over the use of Observable.Create"""

  def subscribeCore(self, observer):
    return self.subscribeRaw(observer, True)

  def subscribeRaw(self, observer, enableSafequard):
    sink = SingleAssignmentDisposable()
    subscription = SingleAssignmentDisposable()

    d = CompositeDisposable(sink, subscription)

    if enableSafequard:
      observer = AutoDetachObserver(observer, d)

    def assignSink(s):
      sink.disposable = s

    def scheduled(_, me):
      subscription.disposable = me.run(observer, subscription, assignSink)
      return Disposable.empty()

    if Scheduler.currentThread.isScheduleRequired():
      Scheduler.currentThread.schedule(self, scheduled)
    else:
      scheduled(None, self)

    return d

  def run(self, observer, cancel, setSink):
    raise NotImplementedError()

class PushToPullAdapter(object):
  def __init__(self, source):
    self.source = source

  def __iter__(self):
    d = SingleAssignmentDisposable()
    res = self.run(d)
    d.disposable = self.source.subscribeSafe(res)
    return res

  def run(self, subscription):
    raise NotImplementedError()
