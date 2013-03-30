from .asObservable import AsObservable
from .buffer import Buffer
from .dematerialize import Dematerialize
from .distinctUntilChanged import DistinctUntilChanged
from .do import Do
from .finallyOp import Finally
from .ignoreElements import IgnoreElements
from .materialize import Materialize
from .scan import ScanWithSeed, ScanWithoutSeed
from .skipLast import SkipLastCount, SkipLastTime
from .takeLast import TakeLastCount, TakeLastTime
from .takeLastBuffer import TakeLastBufferCount, TakeLastBufferTime
from .window import Window

from rx.internal import defaultComparer, identity, noop
from rx.observable import Observable
from rx.scheduler import Scheduler

import itertools


####################
#      Single      #
####################

def asObservable(self):
  assert isinstance(self, Observable)

  if isinstance(self, AsObservable):
    return self.omega()
  else:
    return AsObservable(self)
Observable.asObservable = asObservable

def bufferOp(self, count, skip=None):
  assert isinstance(self, Observable)

  if skip == None:
    return Buffer(self, count, count)
  else:
    return Buffer(self, count, skip)
Observable.buffer = bufferOp

def dematerialize(self):
  assert isinstance(self, Observable)

  if isinstance(self, Materialize):
    return self.dematerialize()
  else:
    return Dematerialize(self)
Observable.dematerialize = dematerialize

def distinctUntilChanged(self, keySelector=identity, equals=defaultComparer):
  assert isinstance(self, Observable)
  assert callable(keySelector)
  assert callable(equals)

  return DistinctUntilChanged(self, keySelector, equals)
Observable.distinctUntilChanged = distinctUntilChanged

def do(self, onNext=noop, onError=noop, onCompleted=noop):
  assert isinstance(self, Observable)
  assert callable(onNext)
  assert callable(onError)
  assert callable(onCompleted)

  return Do(self, onNext, onError, onCompleted)
Observable.do = do

def doFinally(self, action):
  assert isinstance(self, Observable)
  assert callable(action)

  return Finally(self, action)
Observable.doFinally = doFinally

def ignoreElements(self):
  assert isinstance(self, Observable)

  if isinstance(self, IgnoreElements):
    return self.omega()
  else:
    return IgnoreElements(self)
Observable.ignoreElements = ignoreElements

def materialize(self):
  #
  # NOTE: Peephole optimization of xs.Dematerialize().Materialize() should not be performed. It's possible for xs to
  #       contain multiple terminal notifications, which won't survive a Dematerialize().Materialize() chain. In case
  #       a reduction to xs.AsObservable() would be performed, those notification elements would survive.
  #
  assert isinstance(self, Observable)

  return Materialize(self)
Observable.materialize = materialize

def repeatSelf(self, count = None):
  assert isinstance(self, Observable)

  if count == None:
    return Observable.concat(itertools.repeat(self))
  else:
    return Observable.concat(itertools.repeat(self, count))
Observable.repeatSelf = repeatSelf

def retry(self, count = None):
  assert isinstance(self, Observable)

  if count == None:
    return Observable.catchFallback(itertools.repeat(self))
  else:
    return Observable.catchFallback(itertools.repeat(self, count))
Observable.retry = retry

def scan(self, seed=None, accumulator=None):
  assert isinstance(self, Observable)
  assert callable(accumulator)

  if seed == None:
    return ScanWithoutSeed(self, accumulator)
  else:
    return ScanWithSeed(self, seed, accumulator)
Observable.scan = scan

def skipLast(self, count):
  assert isinstance(self, Observable)

  return SkipLastCount(self, count)
Observable.skipLast = skipLast

def skipLastWithTime(self, time, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  return SkipLastTime(self, time, scheduler)
Observable.skipLastWithTime = skipLastWithTime

def startWith(self, *values):
  assert isinstance(self, Observable)

  return Observable.fromIterable(list(values)).concat(self)
Observable.startWith = startWith

def takeLast(self, count, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)

  return TakeLastCount(self, count, scheduler)
Observable.takeLast = takeLast

def takeLastWithTime(self, time, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  return TakeLastTime(self, time, scheduler)
Observable.takeLastWithTime = takeLastWithTime

def takeLastBuffer(self, count):
  assert isinstance(self, Observable)

  return TakeLastBufferCount(self, count)
Observable.takeLastBuffer = takeLastBuffer

def takeLastBufferWithTime(self, time, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  return TakeLastBufferTime(self, time, scheduler)
Observable.takeLastBufferWithTime = takeLastBufferWithTime

def window(self, count, skip=None):
  assert isinstance(self, Observable)

  if skip == None:
    return Window(self, count=count, skip=count)
  else:
    return Window(self, count=count, skip=skip)
Observable.window = window
