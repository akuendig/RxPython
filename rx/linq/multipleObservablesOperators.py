from .amb import Amb
from .catch import CatchException, CatchFallback
from .combineLatest import CombineLatest
from .concat import Concat
from .merge import Merge
from .onErrorResumeNext import OnErrorResumeNext
from .skipUntil import SkipUntilObservable, SkipUntilTime
from .switch import Switch
from .takeUntil import TakeUntilObservable, TakeUntilTime
from .zip import Zip

from rx.observable import Observable
from rx.scheduler import Scheduler

import collections

def flattedSequence(items):
  for item in items:
    isIterable = isinstance(item, collections.Iterable)
    isString = isinstance(item, str)

    if isinstance(item, Observable):
      yield item
    elif isIterable and not isString:
      for element in item:
        yield element
    else:
      yield item

####################
#    Multiple      #
####################

def amb(first, *second):
  assert isinstance(first, Observable)

  for source in second:
    assert isinstance(source, Observable)

    first = Amb(first, source)

  return first
Observable.amb = amb

# def bufferIndividual(self, bufferOpeningSelector, bufferClosingSelector):
#   pass

def catchException(self, handler, exceptionType=Exception):
  assert isinstance(self, Observable)
  assert callable(handler)

  return CatchException(self, handler, exceptionType)
Observable.catchException = catchException

def catchFallback(*sources):
  return CatchFallback(flattedSequence(sources))
Observable.catchFallback = catchFallback

def combineLatest(*sources, resultSelector=tuple):
  assert callable(resultSelector)

  sources = list(flattedSequence(sources))
  return CombineLatest(sources, resultSelector)
Observable.combineLatest = combineLatest

def concat(*sources):
  return Concat(flattedSequence(sources))
Observable.concat = concat

def merge(sourcesObservable, maxConcurrency=0):
  if isinstance(sourcesObservable, Observable):
    return Merge(sourcesObservable, maxConcurrency)
  else:
    sourcesObservable = Observable.fromIterable(sourcesObservable)
    return Merge(sourcesObservable, maxConcurrency)

Observable.merge = merge

def onErrorResumeNext(*sources):
  return OnErrorResumeNext(flattedSequence(sources))
Observable.onErrorResumeNext = onErrorResumeNext

def skipUntil(self, otherOrTime, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  if isinstance(otherOrTime, Observable):
    return SkipUntilObservable(self, otherOrTime)
  else:
    return SkipUntilTime(self, otherOrTime, scheduler)
Observable.skipUntil = skipUntil

def switch(sourcesObservable):
  assert isinstance(sourcesObservable, Observable)

  return Switch(sourcesObservable)
Observable.switch = switch

def takeUntil(self, otherOrTime, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  if isinstance(otherOrTime, Observable):
    return TakeUntilObservable(self, otherOrTime)
  else:
    return TakeUntilTime(self, otherOrTime, scheduler)
Observable.takeUntil = takeUntil

def zipOp(*sources, resultSelector=lambda *x: tuple(x)):
  return Zip(flattedSequence(sources), resultSelector)
Observable.zip = zipOp
