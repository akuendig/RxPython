from .defaultIfEmpty import DefaultIfEmpty
from .distinct import Distinct
from .groupBy import GroupBy
from .groupByUntil import GroupByUntil
from .groupJoin import GroupJoin
from .join import Join
from .ofType import OfType
from .select import Select
from .selectMany import SelectMany
from .skip import SkipCount, SkipTime
from .skipWhile import SkipWhile
from .take import TakeCount, TakeTime
from .takeWhile import TakeWhile
from .where import Where

from rx.internal import identity
from rx.observable import Observable
from rx.scheduler import Scheduler


####################
# StandardSequence #
####################

def defaultIfEmpty(self, default=None):
  assert isinstance(self, Observable)

  return DefaultIfEmpty(self, default)
Observable.defaultIfEmpty = defaultIfEmpty

def distinct(self, keySelector=identity):
  assert isinstance(self, Observable)
  assert callable(keySelector)

  return Distinct(self, keySelector)
Observable.distinct = distinct

def groupBy(self, keySelector=identity, elementSelector=identity):
  assert isinstance(self, Observable)
  assert callable(keySelector)
  assert callable(elementSelector)

  return GroupBy(self, keySelector, elementSelector)
Observable.groupBy = groupBy

def groupByUntil(self, keySelector, elementSelector, durationSelector):
  assert isinstance(self, Observable)
  assert callable(keySelector)
  assert callable(elementSelector)
  assert callable(durationSelector)

  return GroupByUntil(self, keySelector, elementSelector, durationSelector)
Observable.groupByUntil = groupByUntil

def groupJoin(left, right, leftDurationSelector, rightDurationSelector, resultSelector):
  assert isinstance(left, Observable)
  assert isinstance(right, Observable)
  assert callable(leftDurationSelector)
  assert callable(rightDurationSelector)
  assert callable(resultSelector)

  return GroupJoin(left, right, leftDurationSelector, rightDurationSelector, resultSelector)
Observable.groupJoin = groupJoin

def join(left, right, leftDurationSelector, rightDurationSelector, resultSelector):
  assert isinstance(left, Observable)
  assert isinstance(right, Observable)
  assert callable(leftDurationSelector)
  assert callable(rightDurationSelector)
  assert callable(resultSelector)

  return Join(left, right, leftDurationSelector, rightDurationSelector, resultSelector)
Observable.join = join

def ofType(self, tpe):
  assert isinstance(self, Observable)

  return OfType(self, tpe)
Observable.ofType = ofType

def select(self, selector):
  assert isinstance(self, Observable)
  assert callable(selector)

  return Select(self, selector, False)
Observable.select = select

def selectEnumerate(self, selector):
  assert isinstance(self, Observable)
  assert callable(selector)

  return Select(self, selector, True)
Observable.selectEnumerate = selectEnumerate

def selectMany(self, onNext, onError=None, onCompleted=None):
  assert isinstance(self, Observable)

  on = onNext
  oe = onError
  oc = onCompleted

  if not callable(onNext):
    assert isinstance(onNext, Observable)
    on = lambda _: onNext

  if onError != None and not callable(onError):
    assert isinstance(onError, Observable)
    oe = lambda _: onError

  if onCompleted != None and not callable(onCompleted):
    assert isinstance(onCompleted, Observable)
    oc = lambda: onCompleted

  return SelectMany(self, on, oe, oc, False)
Observable.selectMany = selectMany

#inspect.getfullargspec(selector) but not working for partial
def selectManyEnumerate(self, onNext, onError=None, onCompleted=None):
  assert isinstance(self, Observable)

  on = onNext
  oe = onError
  oc = onCompleted

  if not callable(onNext):
    assert isinstance(onNext, Observable)
    on = lambda _, i: onNext

  if onError != None and not callable(onError):
    assert isinstance(onError, Observable)
    oe = lambda _, i: onError

  if onCompleted != None and not callable(onCompleted):
    assert isinstance(onCompleted, Observable)
    oc = lambda _: onCompleted

  return SelectMany(self, on, oe, oc, True)
Observable.selectManyEnumerate = selectManyEnumerate

def skip(self, count):
  assert isinstance(self, Observable)

  if isinstance(self, SkipCount):
    return self.omega(count)

  return SkipCount(self, count)
Observable.skip = skip

def skipWithTime(self, time, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  if isinstance(self, SkipTime):
    return self.omega(time)

  return SkipTime(self, time, scheduler)

def skipWhile(self, predicate):
  assert isinstance(self, Observable)
  assert callable(predicate)

  return SkipWhile(self, predicate, False)
Observable.skipWhile = skipWhile

def skipWhileEnumerate(self, predicate):
  assert isinstance(self, Observable)
  assert callable(predicate)

  return SkipWhile(self, predicate, True)
Observable.skipWhileEnumerate = skipWhileEnumerate

def take(self, count):
  assert isinstance(self, Observable)

  if isinstance(self, TakeCount):
    return self.omega(count)

  return TakeCount(self, count)
Observable.take = take

def takeWithTime(self, time, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  if isinstance(self, TakeTime):
    return self.omega(time)

  return TakeTime(self, time, scheduler)

def takeWhile(self, predicate):
  assert isinstance(self, Observable)
  assert callable(predicate)

  return TakeWhile(self, predicate, False)
Observable.takeWhile = takeWhile

def takeWhileEnumerate(self, predicate):
  assert isinstance(self, Observable)
  assert callable(predicate)

  return TakeWhile(self, predicate, True)
Observable.takeWhileEnumerate = takeWhileEnumerate

def where(self, predicate):
  assert isinstance(self, Observable)
  assert callable(predicate)

  if isinstance(self, Where):
    return self.omega(predicate)
  else:
    return Where(self, predicate, False)
Observable.where = where

def whereEnumerate(self, predicate):
  assert isinstance(self, Observable)
  assert callable(predicate)

  if isinstance(self, Where):
    return self.omega(predicate)
  else:
    return Where(self, predicate, True)
Observable.whereEnumerate = whereEnumerate
