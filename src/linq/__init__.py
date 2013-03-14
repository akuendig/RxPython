from .aggregate import Aggregate
from .all import All
from .any import Any
from .amb import Amb
from .asObservable import AsObservable
from .average import Average
from .buffer import Buffer
from .case import Case
from .catch import CatchException, CatchFallback
from .collect import Collect
from .combineLatest import CombineLatest
from .concat import Concat
from .contains import Contains
from .count import Count
from .defaultIfEmpty import DefaultIfEmpty
from .defer import Defer
from .delay import DelayObservable, DelaySubscription, DelayTime
from .dematerialize import Dematerialize
from .distinct import Distinct
from .distinctUntilChanged import DistinctUntilChanged
from .do import Do
from .doWhile import DoWhile
from .elementAt import ElementAt
from .empty import Empty
from .finallyOp import Finally
from .firstAsync import FirstAsync
from .forEach import ForEach
from .forOp import For
from .generate import Generate
from .getIterator import GetIterator
from .groupBy import GroupBy
from .groupByUntil import GroupByUntil
from .groupJoin import GroupJoin
from .ifOp import If
from .ignoreElements import IgnoreElements
from .isEmpty import IsEmpty
from .join import Join
from .lastAsync import LastAsync
from .latest import Latest
from .materialize import Materialize
from .max import Max
from .maxBy import MaxBy
from .merge import Merge
from .min import Min
from .minBy import MinBy
from .mostRecent import MostRecent
from .multicast import Multicast
from .never import Never
from .next import Next
from .ofType import OfType
from .onErrorResumeNext import OnErrorResumeNext
from .observeOn import ObserveOn
from .range import Range
from .refCount import RefCount
from .repeat import Repeat
from .returnOp import Return
from .sample import SampleWithObservable, SampleWithTime
from .scan import ScanWithSeed, ScanWithoutSeed
from .select import Select
from .selectMany import SelectMany
from .sequenceEqual import SequenceEqual
from .singleAsync import SingleAsync
from .skip import SkipCount, SkipTime
from .skipLast import SkipLastCount, SkipLastTime
from .skipUntil import SkipUntilObservable, SkipUntilTime
from .skipWhile import SkipWhile
from .sum import Sum
from .switch import Switch
from .synchonize import Synchronize
from .take import TakeCount, TakeTime
from .takeLast import TakeLastCount, TakeLastTime
from .takeLastBuffer import TakeLastBufferCount, TakeLastBufferTime
from .takeUntil import TakeUntilObservable, TakeUntilTime
from .takeWhile import TakeWhile
from .throttle import ThrottleObservable, ThrottleTime
from .throw import Throw
from .timeout import TimeoutAbsolute, TimeoutRelative, TimeoutObservable
from .timer import Timer
from .timestamp import TimeStamp
from .toDictionary import ToDictionary
from .toList import ToList
from .toObservable import ToObservable
from .using import Using
from .where import Where
from .whileOp import While
from .window import Window
from .zip import Zip

from disposable import SchedulerDisposable, SerialDisposable, SingleAssignmentDisposable
from observable import AnonymousObservable, ConnectableObservable, Observable
from observer import AnonymousObserver
from scheduler import Scheduler
from subject import AsyncSubject, BehaviorSubject, ReplaySubject, Subject
from internal import defaultComparer, defaultCompareTo, Struct

import sys
from threading import Event

def truePredicate(c): return True

####################
#    Aggreagate    #
####################

def aggregate(self, seed, accumulator, resultSelector=id):
  return Aggregate(self, seed, accumulator, resultSelector)
Observable.aggregate = aggregate

def average(self, selector=id):
  if selector == id:
    return Average(self)
  else:
    return Average(Select(self, selector))
Observable.average = average

Observable.all = lambda self, predicate: All(self, predicate)

def anyOp(self, predicate=truePredicate):
  return Any(self, predicate)
Observable.any = anyOp

Observable.average = lambda self: Average(self)

def contains(self, value, comparer=defaultComparer):
  return Contains(self, value, comparer)
Observable.contains = contains

def count(self, predicate=truePredicate):
  return Count(self, predicate)
Observable.count = count

Observable.elementAt = lambda self, index: ElementAt(self, index, True)
Observable.elementAtOrDefault = lambda self, index: ElementAt(self, index, False)

def firstAsync(self, predicate=truePredicate):
  return FirstAsync(self, predicate, True)
Observable.firstAsync = firstAsync

def firstAsyncOrDefault(self, predicate=truePredicate):
  return FirstAsync(self, predicate, False)
Observable.firstAsyncOrDefault = firstAsyncOrDefault

Observable.isEmpty = lambda self: IsEmpty(self)

def lastAsync(self, predicate=truePredicate):
  return LastAsync(self, predicate, True)
Observable.lastAsync = lastAsync

def lastAsyncOrDefault(self, predicate=truePredicate):
  return LastAsync(self, predicate, False)
Observable.lastAsyncOrDefault = lastAsyncOrDefault

def maxOp(self, compareTo=defaultCompareTo):
  return Max(self, compareTo)
Observable.max = maxOp

def maxBy(self, keySelector, compareTo=defaultCompareTo):
  return MaxBy(self, keySelector, compareTo)
Observable.maxBy = maxBy

def minOp(self, compareTo=defaultCompareTo):
  return Min(self, compareTo)
Observable.min = minOp

def minBy(self, keySelector, compareTo=defaultCompareTo):
  return MinBy(self, keySelector, compareTo)
Observable.minBy = minBy

def sequenceEqual(self, second, compareTo=defaultCompareTo):
  return SequenceEqual(self, second, compareTo)
Observable.sequenceEqual = sequenceEqual

def singleAsync(self, predicate=truePredicate):
  return SingleAsync(self, predicate, True)
Observable.singleAsync = singleAsync

def singleAsyncOrDefault(self, predicate=truePredicate):
  return SingleAsync(self, predicate, False)
Observable.singleAsyncOrDefault = singleAsyncOrDefault

def sumOp(self, selector=id):
  if selector == id:
    return Sum(self)
  else:
    return Sum(Select(self, selector))
Observable.sum = sumOp

def toDictionary(self, keySelector=id, elementSelector=id):
  return ToDictionary(self, keySelector, elementSelector)
Observable.toDictionary = toDictionary

Observable.toList = lambda self: ToList(self)

####################
#     Binding      #
####################

def multicast(self, subject=None, subjectSelector=None, selector=None):
  if subject != None:
    assert subjectSelector == None and selector == None
    return ConnectableObservable(self, subject)
  else:
    assert subjectSelector != None and selector != None
    return Multicast(self, subjectSelector, selector)
Observable.multicast = multicast

def publish(self, selector=None, initialValue=None):
  if selector == None:
    if initialValue == None:
      return self.multicast(Subject())
    else:
      return self.multicast(BehaviorSubject(initialValue))
  else:
    if initialValue == None:
      def sub(): return Subject()
      return self.multicast(subjectSelector=sub, selector=selector)
    else:
      def sub(): return BehaviorSubject(initialValue)
      return self.multicast(subjectSelector=sub, selector=selector)
Observable.publish = publish

def publishLast(self, selector=None):
  if selector == None:
    return self.multicast(AsyncSubject())
  else:
    def sub(): return AsyncSubject()
    return self.multicast(subjectSelector=sub, selector=selector)
Observable.publishLast = publishLast

Observable.refCount = lambda self: RefCount(self)

def replay(self, selector=None, bufferSize=sys.maxsize, window=sys.maxsize, scheduler=Scheduler.currentThread):
  if selector == None:
    return self.multicast(ReplaySubject(bufferSize, window, scheduler))
  else:
    def sub(): return ReplaySubject(bufferSize, window, scheduler)
    return self.multicast(subjectSelector=sub, selector=selector)
Observable.replay = replay

####################
#     Blocking     #
####################

def collect(self, getInitialCollector, merge, getNewCollector=None):
  if getNewCollector == None:
    return Collect(self, getInitialCollector, merge, lambda _: getInitialCollector())
  else:
    return Collect(self, getInitialCollector, merge, getNewCollector)
Observable.collect = collect

def firstOrDefaultInternal(source, throwIfEmpty):
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

  if throwIfEmpty and not state.hasValue:
    raise Exception("Invalid operation, no elements in observable")

  return state.value

def first(self, predicate=None):
  if predicate == None:
    return firstOrDefaultInternal(self, True)
  else:
    return first(Where(self, predicate))
Observable.first = first

def firstOrDefault(self, predicate=None):
  if predicate == None:
    return firstOrDefaultInternal(self, False)
  else:
    return firstOrDefault(Where(self, predicate))
Observable.firstOrDefault = firstOrDefault

def forEach(self, onNext):
  event = Event()
  sink = ForEach.Sink(onNext, lambda: event.set())

  with self.subscribeSafe(sink):
    event.wait()

  if sink.exception != None:
    raise sink.exception
Observable.forEach = forEach

def forEachEnumerate(self, onNext):
  event = Event()
  sink = ForEach.EnumeratingSink(onNext, lambda: event.set())

  with self.subscribeSafe(sink):
    event.wait()

  if sink.exception != None:
    raise sink.exception
Observable.forEachEnumerate = forEachEnumerate

def getIterator(self):
  e = GetIterator()
  return e.run(self)
Observable.getIterator = getIterator
Observable.__iter__ = getIterator

def lastOrDefaultInternal(source, throwIfEmpty):
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

  if throwIfEmpty and not state.hasValue:
    raise Exception("Invalid operation, no elements in observable")

  return state.value

def last(self, predicate=None):
  if predicate == None:
    return lastOrDefaultInternal(self, True)
  else:
    return last(Where(self, predicate))
Observable.last = last

def lastOrDefault(self, predicate=None):
  if predicate == None:
    return lastOrDefaultInternal(self, False)
  else:
    return lastOrDefault(Where(self, predicate))
Observable.lastOrDefault = lastOrDefault

Observable.latest = lambda self: Latest(self)

Observable.mostRecent = lambda self: MostRecent(self)

Observable.next = lambda self: Next(self)


def singleOrDefaultInternal(source, throwIfEmpty):
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

  if throwIfEmpty and not state.hasValue:
    raise Exception("Invalid operation, no elements in observable")

  return state.value

def single(self, predicate=None):
  if predicate == None:
    return singleOrDefaultInternal(self, True)
  else:
    return single(Where(self, predicate))
Observable.single = single

def singleOrDefault(self, predicate=None):
  if predicate == None:
    return singleOrDefaultInternal(self, False)
  else:
    return singleOrDefault(Where(self, predicate))
Observable.singleOrDefault = singleOrDefault

Observable.wait = last

####################
#   Concurrency    #
####################

def subscribeOn(self, scheduler):
  def subscribe(observer):
    m = SingleAssignmentDisposable()
    d = SerialDisposable()
    d.disposable = m

    m.disposable = scheduler.schedule(lambda: s.disposable = SchedulerDisposable(scheduler, source.subscribeSafe(observer)))

    return d

  return AnonymousObservable(subscribe)
Observable.subscribeOn = subscribeOn

Observable.observeOn = lambda self, scheduler: ObserveOn(self, scheduler)

def synchronize(self, gate=None):
  return Synchronize(self, gate)
Observeable.synchronize = synchronize

####################
#   Conversion     #
####################

# From iterable should be done via Observable.Create

# To iterable via __iter__ or getIterator

# To EventSource not possible

# To EventPattern not possible

def toObservable(self, scheduler = Scheduler.iteration):
  return ToObservable(self, scheduler)
Observable.toObservable = toObservable









