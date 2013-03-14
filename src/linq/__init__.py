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

from observable import Observable
from internal import defaultComparer, defaultCompareTo

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





