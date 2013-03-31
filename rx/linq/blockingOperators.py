from .collect import Collect
from .forEach import ForEach
from .getIterator import GetIterator
from .latest import Latest
from .mostRecent import MostRecent
from .next import Next
from .where import Where

from rx.internal import Struct
from rx.observable import Observable
from rx.observer import AnonymousObserver

from threading import Event


####################
#     Blocking     #
####################

def collect(self, getInitialCollector, merge, getNewCollector=None):
  assert isinstance(self, Observable)
  assert callable(getInitialCollector)
  assert callable(merge)

  if getNewCollector == None:
    return Collect(self, getInitialCollector, merge, lambda _: getInitialCollector())
  else:
    assert callable(getNewCollector)

    return Collect(self, getInitialCollector, merge, getNewCollector)
Observable.collect = collect

def firstOrDefaultInternal(source, throwOnEmpty, default):
  state = Struct(
    value=None,
    hasValue=False,
    ex=None,
    event=Event()
  )

  def onNext(value):
    if not state.hasValue:
      state.value = value
    state.hasValue = True
    state.event.set()

  def onError(exception):
    state.ex = exception
    state.event.set()

  def onCompleted():
    state.event.set()

  with source.subscribe(AnonymousObserver(onNext, onError, onCompleted)):
    state.event.wait()

  if state.ex != None:
    raise state.ex

  if not state.hasValue:
    if throwOnEmpty:
      raise Exception("Invalid operation, no elements in observable")
    else:
      return default

  return state.value

def first(self, predicate=None):
  assert isinstance(self, Observable)

  if predicate == None:
    return firstOrDefaultInternal(self, True, None)
  else:
    assert callable(predicate)

    return first(Where(self, predicate, False))
Observable.first = first

def firstOrDefault(self, predicate=None, default=None):
  assert isinstance(self, Observable)

  if predicate == None:
    return firstOrDefaultInternal(self, False, default)
  else:
    assert callable(predicate)

    return firstOrDefault(Where(self, predicate, False), default=default)
Observable.firstOrDefault = firstOrDefault

def forEach(self, onNext):
  assert isinstance(self, Observable)
  assert callable(onNext)

  event = Event()
  sink = ForEach.Sink(onNext, lambda: event.set())

  with self.subscribeSafe(sink):
    event.wait()

  if sink.exception != None:
    raise sink.exception
Observable.forEach = forEach

def forEachEnumerate(self, onNext):
  assert isinstance(self, Observable)
  assert callable(onNext)

  event = Event()
  sink = ForEach.EnumeratingSink(onNext, lambda: event.set())

  with self.subscribeSafe(sink):
    event.wait()

  if sink.exception != None:
    raise sink.exception
Observable.forEachEnumerate = forEachEnumerate

def getIterator(self):
  assert isinstance(self, Observable)

  e = GetIterator()
  return e.run(self)
Observable.getIterator = getIterator
Observable.__iter__ = getIterator

def lastOrDefaultInternal(source, throwOnEmpty, default):
  state = Struct(
    value=None,
    hasValue=False,
    ex=None,
    event=Event()
  )

  def onNext(value):
    state.value = value
    state.hasValue = True

  def onError(exception):
    state.ex = exception
    state.event.set()

  def onCompleted():
    state.event.set()

  with source.subscribe(AnonymousObserver(onNext, onError, onCompleted)):
    state.event.wait()

  if state.ex != None:
    raise state.ex

  if  not state.hasValue:
    if throwOnEmpty:
      raise Exception("Invalid operation, no elements in observable")
    else:
      return default

  return state.value

def last(self, predicate=None):
  assert isinstance(self, Observable)

  if predicate == None:
    return lastOrDefaultInternal(self, True, None)
  else:
    assert callable(predicate)

    return last(Where(self, predicate, False))
Observable.last = last

def lastOrDefault(self, predicate=None, default=None):
  assert isinstance(self, Observable)

  if predicate == None:
    return lastOrDefaultInternal(self, False, default)
  else:
    assert callable(predicate)

    return lastOrDefault(Where(self, predicate, False), default=default)
Observable.lastOrDefault = lastOrDefault

def latest(self):
  assert isinstance(self, Observable)

  return Latest(self)
Observable.latest = latest

def mostRecent(self, initialValue):
  assert isinstance(self, Observable)

  return MostRecent(self, initialValue)
Observable.mostRecent = mostRecent

def next(self):
  assert isinstance(self, Observable)

  return Next(self)
Observable.next = next


def singleOrDefaultInternal(source, throwOnEmpty, default):
  state = Struct(
    value=None,
    hasValue=False,
    ex=None,
    event=Event()
  )

  def onNext(value):
    if state.hasValue:
      state.ex = Exception("Invalid operation, more than one element in observable")
      state.event.set()

    state.value = value
    state.hasValue = True

  def onError(exception):
    state.ex = exception
    state.event.set()

  def onCompleted():
    state.event.set()

  with source.subscribe(AnonymousObserver(onNext, onError, onCompleted)):
    state.event.wait()

  if state.ex != None:
    raise state.ex

  if  not state.hasValue:
    if throwOnEmpty:
      raise Exception("Invalid operation, no elements in observable")
    else:
      return default

  return state.value

def single(self, predicate=None):
  assert isinstance(self, Observable)

  if predicate == None:
    return singleOrDefaultInternal(self, True, None)
  else:
    assert callable(predicate)

    return single(Where(self, predicate), False)
Observable.single = single

def singleOrDefault(self, predicate=None, default=None):
  assert isinstance(self, Observable)

  if predicate == None:
    return singleOrDefaultInternal(self, False, default)
  else:
    assert callable(predicate)

    return singleOrDefault(Where(self, predicate, False), default=default)
Observable.singleOrDefault = singleOrDefault

Observable.wait = last
