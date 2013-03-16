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
from .synchonize import Synchronize
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

from disposable import Disposable, SchedulerDisposable, SerialDisposable, SingleAssignmentDisposable
from observable import AnonymousObservable, ConnectableObservable, Observable
from observer import AnonymousObserver
from scheduler import Scheduler
from subject import AsyncSubject, BehaviorSubject, ReplaySubject, Subject
from internal import defaultComparer, defaultCompareTo, noop, Struct

import itertools
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

####################
#    Creation      #
####################

def create(subscribe):
  def wrapper(observer):
    a = subscribe(observer)

    if isinstance(a, Disposable):
      return a
    else:
      return Disposable.create(a)

  return AnonymousObservable(wrapper)
Observable.create = create

Observable.defer = lambda observableFactory: Defer(observableFactory)

def empty(scheduler=Scheduler.constantTimeOperations):
  return Empty(scheduler)
Observable.empty = empty

def generate(initialState, condition, iterate, resultSelector, scheduler=Scheduler.iteration):
  return Generate(initialState, condition, iterate, resultSelector, scheduler)
Observable.generate = generate

Observable.never = lambda: Never()

def rangeOp(start, count, scheduler=Scheduler.iteration):
  return Range(start, count, scheduler)
Observable.range = rangeOp

def repeat(value, count=None, scheduler=Scheduler.iteration):
  return Repeat(value, count, scheduler)
Observable.repeat = repeat

def returnOp(value, scheduler = Scheduler.constantTimeOperations):
  return Return(value, scheduler)
Observable.ret = returnOp
Observable.returnValue = returnOp

def throw(exception, scheduler=Scheduler.constantTimeOperations):
  return Throw(exception, scheduler)
Observable.throw = throw

Observable.using = lambda resourceFactory, observableFactory: Using(resourceFactory, observableFactory)

####################
#      From***     #
####################

def fromIterable(iterable, scheduler=Scheduler.default):
  return ToObservable(iterable, scheduler)
Observable.fromIterable = fromIterable

def fromEvent(addHandler, removeHandler, scheduler=Scheduler.default):
  return FromEvent(addHandler, removeHandler, scheduler)
Observable.fromEvent = fromEvent

####################
#    Imperative    #
####################

def case(self, sources, schedulerOrDefaultSource=None):
  if schedulerOrDefaultSource == None:
    return Case(self, sources, Empty())
  elif isinstance(schedulerOrDefaultSource, Scheduler):
    return Case(self, sources, Empty(schedulerOrDefaultSource))
  else:
    return Case(self, sources, schedulerOrDefaultSource)
Observable.case = case

Observable.doWhile = lambda self, condition: DoWhile(self, condition)

Observable.iterableFor = lambda source, resultSelector: For(source, resultSelector)

def branch(condition, thenSource, schedulerOrElseSource=None):
  if schedulerOrElseSource == None:
    return If(condition, thenSource, Empty())
  elif isinstance(schedulerOrElseSource, Scheduler):
    return If(condition, thenSource, Empty(schedulerOrElseSource))
  else:
    return If(condition, thenSource, schedulerOrElseSource)
Observable.branch = branch

Observable.loop = lambda condition, source: While(condition, source)

####################
#      Joins       #
####################

####################
#    Multiple      #
####################

def amb(first, *second):
  for source in second:
    first = Amb(first, source)
Observable.amb = amb

# def bufferWithSelector(self, bufferOpeningSelector, bufferClosingSelector):
#   pass

Observable.catchException = lambda self, handler: CatchException(self, handler)

def catchFallback(self, *sources):
  if len(sources) == 1:
    try:
      sources = iter(sources[0])
    except TypeError:
      sources = [sources[0]]
  else:
    sources = iter(sources)

  return CatchFallback(self, sources)
Observable.catchFallback = catchFallback

def combineLatest(sources, resultSelector=list):
  return CombineLatest(list(sources), resultSelector)
Observable.combineLatest = combineLatest

Observable.concat = lambda sources: Concat(sources)

def merge(sources, maxConcurrency=0):
  return Merge(sources, maxConcurrency)
Observable.merge = merge

def onErrorResumeNext(*sources):
  if len(sources) == 1:
    try:
      sources = iter(sources[0])
    except TypeError:
      sources = [sources[0]]
  else:
    sources = iter(sources)

  return OnErrorResumeNext(sources)
Observable.onErrorResumeNext = onErrorResumeNext

def skipUntil(self, otherOrTime, scheduler=Scheduler.timeBasedOperation):
  if isinstance(otherOrTime, Observable):
    return SkipUntilObservable(self, otherOrTime)
  else:
    return SkipUntilTime(self, otherOrTime, scheduler)
Observable.skipUntil = skipUntil

Observable.switch = lambda sources: Switch(list(sources))

def takeUntil(self, otherOrTime, scheduler=Scheduler.timeBasedOperation):
  if isinstance(otherOrTime, Observable):
    return TakeUntilObservable(self, otherOrTime)
  else:
    return TakeUntilTime(self, otherOrTime, scheduler)
Observable.takeUntil = takeUntil

def zipOp(*sources):
  if len(sources) == 1:
    try:
      sources = iter(sources[0])
    except TypeError:
      sources = [sources[0]]
  else:
    sources = iter(sources)

  return Zip(sources)
Observable.zip = zipOp

####################
#      Single      #
####################

def asObservable(self):
  if isinstance(self, AsObservable):
    return self.omega()
  else:
    return AsObservable(self)
Observable.asObservable = asObservable

def bufferOp(self, count, skip=None):
  if skip == None:
    return Buffer(self, count, count)
  else:
    return Buffer(self, count, skip)
Observable.buffer = bufferOp

def dematerialize(self):
  if isinstance(self, Materialize):
    return self.dematerialize()
  else:
    return Dematerialize(self)
Observable.dematerialize = dematerialize

def distinctUntilChanged(self, keySelector=id, equals=defaultComparer):
  return DistinctUntilChanged(self, keySelector, equals)
Observable.distinctUntilChanged = distinctUntilChanged

def do(self, onNext=noop, onError=noop, onCompleted=noop):
  return Do(self, onNext, onError, onCompleted)

Observable.fin = lambda self, action: Finally(self, action)
Observable.finalAction = Observable.fin

def ignoreElements(self):
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
  return Materialize(self)
Observable.materialize = materialize

def repeatSelf(self, count = None):
  if count == None:
    return Observable.concat(itertools.repeat(self))
  else:
    return Observable.concat(itertools.repeat(self, count))
Observable.repeatSelf = repeatSelf

def retry(self, count = None):
  if count == None:
    return Observable.catchFallback(itertools.repeat(self))
  else:
    return Observable.catchFallback(itertools.repeat(self, count))
Observable.retry = retry

def scan(self, seed=None, accumulator=None):
  if seed == None:
    return ScanWithoutSeed(self, accumulator)
  else:
    return ScanWithSeed(self, seed, accumulator)
Observable.scan = scan

def skipLast(self, countOrTime, scheduler=Scheduler.timeBasedOperation):
  if isinstance(countOrTime, int):
    return SkipLastCount(self, countOrTime)
  else:
    return SkipLastTime(self, countOrTime, scheduler)
Observable.skipLast = skipLast

def startWith(self, *values):
  if len(values) == 1:
    try:
      values = iter(values[0])
    except TypeError:
      values = [values[0]]
  else:
    values = iter(values)

  return Observable.fromIterable(values).concat(self)

def takeLast(self, countOrTime, scheduler=Scheduler.timeBasedOperation):
  if isinstance(countOrTime, int):
    return TakeLastCount(self, countOrTime)
  else:
    return TakeLastTime(self, countOrTime, scheduler)
Observable.takeLast = takeLast

def window(self, count, skip=None):
  if skip == None:
    return Window(self, count=count, skip=count)
  else:
    return Window(self, count=count, skip=skip)
Observable.window = window

####################
# StandardSequence #
####################

Observable.defaultIfEmpty = lambda self, default: DefaultIfEmpty(self, defaultValue)

def distinct(self, keySelector=id):
  return Distinct(self, keySelector)
Observable.distinct = distinct

def groupBy(self, keySelector=id, elementSelector=id):
  return GroupBy(self, keySelector, elementSelector)
Observable.groupBy = groupBy

def groupByUntil(self, keySelector, elementSelector, durationSelector):
  return GroupByUntil(self, keySelector, elementSelector, durationSelector)
Observable.groupByUntil = groupByUntil

def groupJoin(left, right, leftDurationSelector, rightDurationSelector, resultSelector):
  return GroupJoin(left, right, leftDurationSelector, rightDurationSelector, resultSelector)
Observable.groupJoin = groupJoin

def join(left, right, leftDurationSelector, rightDurationSelector, resultSelector):
  return Join(left, right, leftDurationSelector, rightDurationSelector, resultSelector)
Observable.join = join

Observable.ofType = lambda self, tpe: OfType(self, tpe)

Observable.select = lambda self, selector: Select(self, selector, False)

Observable.selectEnumrate = lambda self, selector: Select(self, selector, True)

def selectMany(self, selector):
  if callable(selector):
    return SelectMany(self, selector, False)
  else:
    return SelectMany(self, lambda _: selector, False)
Observable.selectMany = selectMany

#inspect.getfullargspec(selector) but not working for partial
def selectManyEnumerate(self, selector):
  if callable(selector):
    return SelectMany(self, selector, True)
  else:
    return SelectMany(self, lambda _: selector, True)
Observable.selectManyEnumerate = selectManyEnumerate

def skip(self, countOrTime, scheduler=Scheduler.timeBasedOperation):
  if isinstance(self, Skip):
    return self.omega(countOrTime)

  if isinstance(countOrTime, int):
    return SkipCount(self, countOrTime)
  else:
    return SkipTime(self, countOrTime, scheduler)
Observable.skip = skip

Observable.skipWhile = lambda self, predicate: SkipWhile(self, predicate, False)

Observable.skipWhileEnumerate = lambda self, predicate: SkipWhile(self, predicate, True)

def take(self, countOrTime):
  if isinstance(self, Take):
    return self.omega(countOrTime)

  if isinstance(countOrTime, int):
    return TakeCount(self, countOrTime)
  else:
    return TakeTime(self, countOrTime)
Observable.take = take

Observable.takeWhile = lambda self, predicate: TakeWhile(self, predicate, False)

Observable.takeWhileEnumerate = lambda self, predicate: TakeWhile(self, predicate, True)

def where(self, predicate):
  if isinstance(self, Where):
    return self.omega(predicate)
  else:
    return Where(self, predicate)
Observable.where = where

####################
#       Time       #
####################

def bufferWithTime(self, timeSpan, timeShift=None, scheduler=Scheduler.timeBasedOperation):
  if timeShift == None:
    timeShift = timeSpan
  return Buffer(timeSpan=timeSpan, timeShift=timeShift, scheduler=scheduler)
Observable.bufferWithTime = bufferWithTime

def bufferWithTimeAndCount(self, timeSpan, count=None, scheduler=Scheduler.timeBasedOperation):
  if count == None:
    count = timeSpan
  return Buffer(timeSpan=timeSpan, count=count, scheduler=scheduler)
Observable.bufferWithTimeAndCount = bufferWithTimeAndCount

def delayRelative(self, dueTime, scheduler=Scheduler.timeBasedOperation):
  return DelayTime(self, dueTime, False, scheduler)
Observable.delayRelative = delayRelative

def delayAbsolute(self, dueTime, scheduler=Scheduler.timeBasedOperation):
  return DelayTime(self, dueTime, True, scheduler)
Observable.delayAbsolute = delayAbsolute

def delayIndividual(self, subscriptionDelay, delayDurationSelector):
  return DelayObservable(self, subscriptionDelay, delayDurationSelector)
Observable.delayIndividual = delayIndividual

def delaySubscriptionRelative(self, dueTime, scheduler=Scheduler.timeBasedOperation):
  return DelaySubscriptionTime(self, dueTime, False, scheduler)
Observable.delaySubscriptionRelative = delaySubscriptionRelative

def delaySubscriptionAbsolute(self, dueTime, scheduler=Scheduler.timeBasedOperation):
  return DelaySubscriptionTime(self, dueTime, True, scheduler)
Observable.delaySubscriptionAbsolute = delaySubscriptionAbsolute

def generateRelative(initialState, condition, iterate, resultSelector, timeSelector, scheduler=Scheduler.timeBasedOperation):
  return Generate(initialState, condition, iterate, resultSelector, timeSelector, False, scheduler)
Observable.generateRelative = generateRelative

def generateAbsolute(initialState, condition, iterate, resultSelector, timeSelector, scheduler=Scheduler.timeBasedOperation):
  return Generate(initialState, condition, iterate, resultSelector, timeSelector, True, scheduler)
Observable.generateAbsolute = generateAbsolute

def interval(period, scheduler=Scheduler.timeBasedOperation):
  return Timer(period, period, scheduler)
Observable.interval = interval

def sampleWithTime(self, interval, scheduler=Scheduler.timeBasedOperation):
  return SampleWithTime(self, interval, scheduler)
Observable.sampleWithTime = sampleWithTime

Observable.sampleWithObservable = lambda self, sampler: SampleWithObservable(self, sampler)

def throttle(self, dueTime, scheduler=Scheduler.timeBasedOperation):
  return ThrottleTime(self, dueTime, scheduler)
Observable.throttle = throttle

Observable.throttleIndividual = lambda self, durationSelector: ThrottleObservable(self, durationSelector)

def timeInterval(self, scheduler=Scheduler.timeBasedOperation):
  return TimeInterval(self, scheduler)
Observable.timeInterval = timeInterval

def timeoutRelative(self, dueTime, other=None, scheduler=Scheduler.timeBasedOperation):
  if other == None:
    other = Observable.throw(Exception("Timeout in observable"))

  return TimeoutRelative(self, dueTime, other, scheduler)
Observable.timeoutRelative = timeoutRelative

def timeoutAbsolute(self, dueTime, other=None, scheduler=Scheduler.timeBasedOperation):
  if other == None:
    other = Observable.throw(Exception("Timeout in observable"))

  return TimeoutAbsolute(self, dueTime, other, scheduler)
Observable.timeoutAbsolute = timeoutAbsolute

def timeoutIndividual(self, dueTime, durationSelector, firstTimeout=None, other=None):
  if firstTimeout == None:
    firstTimeout = Observable.never()
  if other == None:
    other = Observable.throw(Exception("Timeout in observable"))

  return TimeoutObservable(self, dueTime, firstTimeout, other)
Observable.timeoutIndividual = timeoutIndividual

def timerRelative(dueTime, period=None, scheduler=Scheduler.timeBasedOperation):
  return Timer(dueTime, False, period, scheduler)
Observable.timerRelative = timerRelative

def timerAbsolute(dueTime, period=None, scheduler=Scheduler.timeBasedOperation):
  return Timer(dueTime, True, period, scheduler)
Observable.timerAbsolute = timerAbsolute

def timeStamp(self, scheduler=Scheduler.timeBasedOperation):
  return TimeStamp(self, scheduler)
Observable.timeStamp = timeStamp

def windowWithTime(self, timeSpan, timeShift=None, scheduler=Scheduler.timeBasedOperation):
  if timeShift == None:
    timeShift = timeSpan
  return Window(timeSpan=timeSpan, timeShift=timeShift, scheduler=scheduler)
Observable.windowWithTime = windowWithTime

def windowWithTimeAndCount(self, timeSpan, count=None, scheduler=Scheduler.timeBasedOperation):
  if count == None:
    count = timeSpan
  return Window(timeSpan=timeSpan, count=count, scheduler=scheduler)
Observable.windowWithTimeAndCount = windowWithTimeAndCount







