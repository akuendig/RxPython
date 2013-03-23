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
from .fromEvent import FromEvent
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
from .synchronize import Synchronize
from .take import TakeCount, TakeTime
from .takeLast import TakeLastCount, TakeLastTime
from .takeLastBuffer import TakeLastBufferCount, TakeLastBufferTime
from .takeUntil import TakeUntilObservable, TakeUntilTime
from .takeWhile import TakeWhile
from .throttle import ThrottleObservable, ThrottleTime
from .throw import Throw
from .timeInterval import TimeInterval
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

from rx.disposable import Disposable, SchedulerDisposable, SerialDisposable, SingleAssignmentDisposable
from rx.internal import defaultComparer, defaultCompareTo, identity, noop, Struct
from rx.observable import AnonymousObservable, ConnectableObservable, Observable
from rx.observer import AnonymousObserver
from rx.scheduler import Scheduler
from rx.subject import AsyncSubject, BehaviorSubject, ReplaySubject, Subject

import itertools
import sys
import collections
from threading import Event

def truePredicate(c): return True

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
#    Aggreagate    #
####################

def aggregate(self, seed, accumulator, resultSelector=identity):
  assert isinstance(self, Observable)
  assert callable(accumulator)
  assert callable(resultSelector)

  return Aggregate(self, seed, accumulator, resultSelector)
Observable.aggregate = aggregate

def allOp(self, predicate):
  assert isinstance(self, Observable)
  assert callable(predicate)

  return All(self, predicate)
Observable.all = allOp

def anyOp(self, predicate=truePredicate):
  assert isinstance(self, Observable)
  assert callable(predicate)

  return Any(self, predicate)
Observable.any = anyOp

def average(self, selector=identity):
  assert isinstance(self, Observable)
  assert callable(selector)

  if selector == identity:
    return Average(self)
  else:
    return Average(Select(self, selector))
Observable.average = average

def contains(self, value, comparer=defaultComparer):
  assert isinstance(self, Observable)
  assert callable(comparer)

  return Contains(self, value, comparer)
Observable.contains = contains

def count(self, predicate=truePredicate):
  assert isinstance(self, Observable)
  assert callable(predicate)

  return Count(self, predicate)
Observable.count = count

def elementAt(self, index):
  assert isinstance(self, Observable)

  return ElementAt(self, index, True, None)
Observable.elementAt = elementAt

def elementAtOrDefault(self, index, default=None):
  assert isinstance(self, Observable)

  return ElementAt(self, index, False, default)
Observable.elementAtOrDefault = elementAtOrDefault

def firstAsync(self, predicate=truePredicate):
  assert isinstance(self, Observable)
  assert callable(predicate)

  return FirstAsync(self, predicate, True, None)
Observable.firstAsync = firstAsync

def firstAsyncOrDefault(self, predicate=truePredicate, default=None):
  assert isinstance(self, Observable)
  assert callable(predicate)

  return FirstAsync(self, predicate, False, default)
Observable.firstAsyncOrDefault = firstAsyncOrDefault

def isEmpty(self):
  assert isinstance(self, Observable)

  return IsEmpty(self)
Observable.isEmpty = isEmpty

def lastAsync(self, predicate=truePredicate):
  assert isinstance(self, Observable)
  assert callable(predicate)

  return LastAsync(self, predicate, True, None)
Observable.lastAsync = lastAsync

def lastAsyncOrDefault(self, predicate=truePredicate, default=None):
  assert isinstance(self, Observable)
  assert callable(predicate)

  return LastAsync(self, predicate, False, default)
Observable.lastAsyncOrDefault = lastAsyncOrDefault

def maxOp(self, compareTo=defaultCompareTo):
  assert isinstance(self, Observable)
  assert callable(compareTo)

  return Max(self, compareTo)
Observable.max = maxOp

def maxBy(self, keySelector, compareTo=defaultCompareTo):
  assert isinstance(self, Observable)
  assert callable(keySelector)
  assert callable(compareTo)

  return MaxBy(self, keySelector, compareTo)
Observable.maxBy = maxBy

def minOp(self, compareTo=defaultCompareTo):
  assert isinstance(self, Observable)
  assert callable(compareTo)

  return Min(self, compareTo)
Observable.min = minOp

def minBy(self, keySelector, compareTo=defaultCompareTo):
  assert isinstance(self, Observable)
  assert callable(keySelector)
  assert callable(compareTo)

  return MinBy(self, keySelector, compareTo)
Observable.minBy = minBy

def sequenceEqual(first, second, compareTo=defaultComparer):
  assert isinstance(first, Observable)
  assert isinstance(second, Observable)
  assert callable(compareTo)

  return SequenceEqual(first, second, compareTo)
Observable.sequenceEqual = sequenceEqual

def singleAsync(self, predicate=truePredicate):
  assert isinstance(self, Observable)
  assert callable(predicate)

  return SingleAsync(self, predicate, True, None)
Observable.singleAsync = singleAsync

def singleAsyncOrDefault(self, predicate=truePredicate, default=None):
  assert isinstance(self, Observable)
  assert callable(predicate)

  return SingleAsync(self, predicate, False, default)
Observable.singleAsyncOrDefault = singleAsyncOrDefault

def sumOp(self, selector=identity):
  assert isinstance(self, Observable)
  assert callable(selector)

  if selector == identity:
    return Sum(self)
  else:
    return Sum(Select(self, selector))
Observable.sum = sumOp

def toDictionary(self, keySelector=identity, elementSelector=identity):
  assert isinstance(self, Observable)
  assert callable(keySelector)
  assert callable(elementSelector)

  return ToDictionary(self, keySelector, elementSelector)
Observable.toDictionary = toDictionary

def toList(self):
  assert isinstance(self, Observable)

  return ToList(self)
Observable.toList = toList

####################
#     Binding      #
####################

def multicast(self, subject):
  assert isinstance(self, Observable)
  assert isinstance(subject, Observable)

  return ConnectableObservable(self, subject)
Observable.multicast = multicast

def multicastIndividual(self, subjectSelector, selector):
  assert isinstance(self, Observable)
  assert callable(subjectSelector)
  assert callable(selector)

  return Multicast(self, subjectSelector, selector)
Observable.multicastIndividual = multicastIndividual

def publish(self, initialValue=None):
  assert isinstance(self, Observable)

  if initialValue == None:
    return self.multicast(Subject())
  else:
    return self.multicast(BehaviorSubject(initialValue))
Observable.publish = publish

def publishIndividual(self, selector, initialValue=None):
  assert isinstance(self, Observable)
  assert callable(selector)

  if initialValue == None:
    def sub(): return Subject()
    return self.multicastIndividual(sub, selector)
  else:
    def sub(): return BehaviorSubject(initialValue)
    return self.multicastIndividual(sub, selector)
Observable.publishIndividual = publishIndividual

def publishLast(self, selector=None):
  assert isinstance(self, Observable)

  if selector == None:
    return self.multicast(AsyncSubject())
  else:
    assert callable(selector)

    def sub(): return AsyncSubject()
    return self.multicastIndividual(sub, selector)
Observable.publishLast = publishLast

def refCount(self):
  assert isinstance(self, Observable)

  return RefCount(self)
Observable.refCount = refCount

def replay(self, selector=None, bufferSize=sys.maxsize, window=sys.maxsize, scheduler=Scheduler.currentThread):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  if selector == None:
    return self.multicast(ReplaySubject(bufferSize, window, scheduler))
  else:
    assert callable(selector)

    def sub(): return ReplaySubject(bufferSize, window, scheduler)
    return self.multicastIndividual(sub, selector)
Observable.replay = replay

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

def mostRecent(self):
  assert isinstance(self, Observable)

  return MostRecent(self)
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

####################
#   Concurrency    #
####################

def subscribeOn(self, scheduler):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  def subscribe(observer):
    m = SingleAssignmentDisposable()
    d = SerialDisposable()
    d.disposable = m

    def action():
      d.disposable = SchedulerDisposable(scheduler, self.subscribeSafe(observer))

    m.disposable = scheduler.schedule(action)

    return d

  return AnonymousObservable(subscribe)
Observable.subscribeOn = subscribeOn

def observeOn(self, scheduler):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  return ObserveOn(self, scheduler)
Observable.observeOn = observeOn

def synchronize(self, gate=None):
  assert isinstance(self, Observable)

  return Synchronize(self, gate)
Observable.synchronize = synchronize

####################
#   Conversion     #
####################

# From iterable should be done via Observable.Create

# To iterable via __iter__ or getIterator

# To EventSource not possible

# To EventPattern not possible

def toObservable(self, scheduler = Scheduler.iteration):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  return ToObservable(self, scheduler)
Observable.toObservable = toObservable

####################
#    Creation      #
####################

def create(subscribe):
  assert callable(subscribe)

  def wrapper(observer):
    a = subscribe(observer)

    if isinstance(a, Disposable):
      return a
    else:
      return Disposable.create(a)

  return AnonymousObservable(wrapper)
Observable.create = create

def defer(observableFactory):
  assert callable(observableFactory)

  return Defer(observableFactory)
Observable.defer = defer

def empty(scheduler=Scheduler.constantTimeOperations):
  assert isinstance(scheduler, Scheduler)

  return Empty(scheduler)
Observable.empty = empty

def generate(initialState, condition, iterate, resultSelector, scheduler=Scheduler.iteration):
  assert callable(condition)
  assert callable(iterate)
  assert callable(resultSelector)
  assert isinstance(scheduler, Scheduler)

  return Generate(initialState, condition, iterate, resultSelector, None, None, scheduler)
Observable.generate = generate

def never():
  return Never()
Observable.never = never

def rangeOp(start, count, scheduler=Scheduler.iteration):
  assert isinstance(scheduler, Scheduler)

  return Range(start, count, scheduler)
Observable.range = rangeOp

def repeat(value, count=None, scheduler=Scheduler.iteration):
  assert isinstance(scheduler, Scheduler)

  return Repeat(value, count, scheduler)
Observable.repeat = repeat

def returnOp(value, scheduler = Scheduler.constantTimeOperations):
  assert isinstance(scheduler, Scheduler)

  return Return(value, scheduler)
Observable.returnValue = returnOp

def throw(exception, scheduler=Scheduler.constantTimeOperations):
  assert isinstance(scheduler, Scheduler)

  return Throw(exception, scheduler)
Observable.throw = throw

def using(resourceFactory, observableFactory):
  assert callable(resourceFactory)
  assert callable(observableFactory)

  return Using(resourceFactory, observableFactory)
Observable.using = using

####################
#      From***     #
####################

def fromIterable(iterable, scheduler=Scheduler.default):
  assert isinstance(iterable, collections.Iterable)
  assert isinstance(scheduler, Scheduler)

  return ToObservable(iterable, scheduler)
Observable.fromIterable = fromIterable

def fromEvent(addHandler, removeHandler, scheduler=Scheduler.default):
  assert callable(addHandler)
  assert callable(removeHandler)
  assert isinstance(scheduler, Scheduler)

  return FromEvent(addHandler, removeHandler, scheduler)
Observable.fromEvent = fromEvent

####################
#    Imperative    #
####################

def case(selector, sources, schedulerOrDefaultSource=None):
  assert callable(selector)
  assert isinstance(sources, dict)

  if schedulerOrDefaultSource == None:
    return Case(selector, sources, empty())
  elif isinstance(schedulerOrDefaultSource, Scheduler):
    return Case(selector, sources, empty(schedulerOrDefaultSource))
  else:
    assert isinstance(schedulerOrDefaultSource, Observable)

    return Case(selector, sources, schedulerOrDefaultSource)
Observable.case = case

def doWhile(self, condition):
  assert isinstance(self, Observable)
  assert callable(condition)

  return DoWhile(self, condition)
Observable.doWhile = doWhile

def iterableFor(iterable, resultSelector):
  assert isinstance(iterable, collections.Iterable)
  assert callable(resultSelector)

  return For(iterable, resultSelector)
Observable.iterableFor = iterableFor

def branch(condition, thenSource, schedulerOrElseSource=None):
  assert callable(condition)
  assert isinstance(thenSource, Observable)

  if schedulerOrElseSource == None:
    return If(condition, thenSource, empty())
  elif isinstance(schedulerOrElseSource, Scheduler):
    return If(condition, thenSource, empty(schedulerOrElseSource))
  else:
    assert isinstance(schedulerOrElseSource, Observable)

    return If(condition, thenSource, schedulerOrElseSource)
Observable.branch = branch

def loop(source, condition):
  assert isinstance(source, Observable)
  assert callable(condition)

  return While(source, condition)
Observable.loop = loop

####################
#      Joins       #
####################

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

def catchException(self, handler):
  assert isinstance(self, Observable)
  assert callable(handler)

  return CatchException(self, handler)
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
  assert isinstance(sourcesObservable, Observable)

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

def zipOp(*sources):
  return Zip(flattedSequence(sources))
Observable.zip = zipOp

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

def skipLast(self, countOrTime, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  if isinstance(countOrTime, int):
    return SkipLastCount(self, countOrTime)
  else:
    return SkipLastTime(self, countOrTime, scheduler)
Observable.skipLast = skipLast

def startWith(self, *values):
  assert isinstance(self, Observable)

  if len(values) == 1:
    first = values[0]

    if isinstance(first, Observable):
      values = [first]
    else:
      try:
        values = iter(first)
      except TypeError:
        values = [first]
  else:
    values = iter(values)

  return Observable.fromIterable(values).concat(self)
Observable.startWith = startWith

def takeLast(self, countOrTime, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  if isinstance(countOrTime, int):
    return TakeLastCount(self, countOrTime)
  else:
    return TakeLastTime(self, countOrTime, scheduler)
Observable.takeLast = takeLast

def takeLastBuffer(self, countOrTime, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  if isinstance(countOrTime, int):
    return TakeLastBufferCount(self, countOrTime)
  else:
    return TakeLastBufferTime(self, countOrTime, scheduler)
Observable.takeLastBuffer = takeLastBuffer

def window(self, count, skip=None):
  assert isinstance(self, Observable)

  if skip == None:
    return Window(self, count=count, skip=count)
  else:
    return Window(self, count=count, skip=skip)
Observable.window = window

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

def selectMany(self, onNext, onError=noop, onCompleted=noop):
  assert isinstance(self, Observable)
  assert callable(onNext)
  assert callable(onError)
  assert callable(onCompleted)

  if callable(onNext):
    return SelectMany(self, onNext, onError, onCompleted, False)
  else:
    return SelectMany(self, onNext, onError, onCompleted, False)
Observable.selectMany = selectMany

#inspect.getfullargspec(selector) but not working for partial
def selectManyEnumerate(self, onNext, onError=noop, onCompleted=noop):
  assert isinstance(self, Observable)
  assert callable(onNext)
  assert callable(onError)
  assert callable(onCompleted)

  if callable(onNext):
    return SelectMany(self, onNext, onError, onCompleted, True)
  else:
    return SelectMany(self, onNext, onError, onCompleted, True)
Observable.selectManyEnumerate = selectManyEnumerate

def skip(self, countOrTime, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  if isinstance(self, SkipCount) or isinstance(self, SkipTime):
    return self.omega(countOrTime)

  if isinstance(countOrTime, int):
    return SkipCount(self, countOrTime)
  else:
    return SkipTime(self, countOrTime, scheduler)
Observable.skip = skip

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

def take(self, countOrTime):
  assert isinstance(self, Observable)

  if isinstance(self, TakeCount) or isinstance(self, TakeTime):
    return self.omega(countOrTime)

  if isinstance(countOrTime, int):
    return TakeCount(self, countOrTime)
  else:
    return TakeTime(self, countOrTime)
Observable.take = take

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
    return Where(self, predicate)
Observable.where = where

####################
#       Time       #
####################

def bufferWithTime(self, timeSpan, timeShift=None, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  if timeShift == None:
    timeShift = timeSpan
  return Buffer(timeSpan=timeSpan, timeShift=timeShift, scheduler=scheduler)
Observable.bufferWithTime = bufferWithTime

def bufferWithTimeAndCount(self, timeSpan, count=None, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  if count == None:
    count = timeSpan
  return Buffer(timeSpan=timeSpan, count=count, scheduler=scheduler)
Observable.bufferWithTimeAndCount = bufferWithTimeAndCount

def delayRelative(self, dueTime, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  return DelayTime(self, dueTime, False, scheduler)
Observable.delayRelative = delayRelative

def delayAbsolute(self, dueTime, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  return DelayTime(self, dueTime, True, scheduler)
Observable.delayAbsolute = delayAbsolute

def delayIndividual(self, subscriptionDelay, delayDurationSelector):
  assert isinstance(self, Observable)
  assert callable(delayDurationSelector)

  return DelayObservable(self, subscriptionDelay, delayDurationSelector)
Observable.delayIndividual = delayIndividual

def delaySubscriptionRelative(self, dueTime, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  return DelaySubscription(self, dueTime, False, scheduler)
Observable.delaySubscriptionRelative = delaySubscriptionRelative

def delaySubscriptionAbsolute(self, dueTime, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  return DelaySubscription(self, dueTime, True, scheduler)
Observable.delaySubscriptionAbsolute = delaySubscriptionAbsolute

def generateRelative(initialState, condition, iterate, resultSelector, timeSelector, scheduler=Scheduler.timeBasedOperation):
  assert callable(condition)
  assert callable(iterate)
  assert callable(resultSelector)
  assert callable(timeSelector)
  assert isinstance(scheduler, Scheduler)

  return Generate(initialState, condition, iterate, resultSelector, timeSelector, False, scheduler)
Observable.generateRelative = generateRelative

def generateAbsolute(initialState, condition, iterate, resultSelector, timeSelector, scheduler=Scheduler.timeBasedOperation):
  assert callable(condition)
  assert callable(iterate)
  assert callable(resultSelector)
  assert callable(timeSelector)
  assert isinstance(scheduler, Scheduler)

  return Generate(initialState, condition, iterate, resultSelector, timeSelector, True, scheduler)
Observable.generateAbsolute = generateAbsolute

def interval(period, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(scheduler, Scheduler)

  return Timer(period, period, scheduler)
Observable.interval = interval

def sampleWithTime(self, interval, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  return SampleWithTime(self, interval, scheduler)
Observable.sampleWithTime = sampleWithTime

def sampleWithObservable(self, sampler):
  assert isinstance(self, Observable)
  assert isinstance(sampler, Observable)

  return SampleWithObservable(self, sampler)
Observable.sampleWithObservable = sampleWithObservable

def throttle(self, dueTime, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  return ThrottleTime(self, dueTime, scheduler)
Observable.throttle = throttle

def throttleIndividual(self, durationSelector):
  assert isinstance(self, Observable)
  assert callable(durationSelector)

  return ThrottleObservable(self, durationSelector)
Observable.throttleIndividual = throttleIndividual

def timeInterval(self, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  return TimeInterval(self, scheduler)
Observable.timeInterval = timeInterval

def timeoutRelative(self, dueTime, other=None, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  if other == None:
    other = Observable.throw(Exception("Timeout in observable"))

  assert isinstance(other, Observable)

  return TimeoutRelative(self, dueTime, other, scheduler)
Observable.timeoutRelative = timeoutRelative

def timeoutAbsolute(self, dueTime, other=None, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  if other == None:
    other = Observable.throw(Exception("Timeout in observable"))

  assert isinstance(other, Observable)

  return TimeoutAbsolute(self, dueTime, other, scheduler)
Observable.timeoutAbsolute = timeoutAbsolute

def timeoutIndividual(self, dueTime, durationSelector, firstTimeout=None, other=None):
  assert isinstance(self, Observable)

  if firstTimeout == None:
    firstTimeout = Observable.never()
  if other == None:
    other = Observable.throw(Exception("Timeout in observable"))

  assert isinstance(firstTimeout, Observable)
  assert isinstance(other, Observable)

  return TimeoutObservable(self, dueTime, firstTimeout, other)
Observable.timeoutIndividual = timeoutIndividual

def timerRelative(dueTime, period=None, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(scheduler, Scheduler)

  return Timer(dueTime, False, period, scheduler)
Observable.timerRelative = timerRelative

def timerAbsolute(dueTime, period=None, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(scheduler, Scheduler)

  return Timer(dueTime, True, period, scheduler)
Observable.timerAbsolute = timerAbsolute

def timeStamp(self, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  return TimeStamp(self, scheduler)
Observable.timeStamp = timeStamp

def windowWithTime(self, timeSpan, timeShift=None, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  if timeShift == None:
    timeShift = timeSpan
  return Window(timeSpan=timeSpan, timeShift=timeShift, scheduler=scheduler)
Observable.windowWithTime = windowWithTime

def windowWithTimeAndCount(self, timeSpan, count=None, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  if count == None:
    count = timeSpan
  return Window(timeSpan=timeSpan, count=count, scheduler=scheduler)
Observable.windowWithTimeAndCount = windowWithTimeAndCount







