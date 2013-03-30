from .aggregate import Aggregate
from .all import All
from .any import Any
from .average import Average
from .contains import Contains
from .count import Count
from .elementAt import ElementAt
from .firstAsync import FirstAsync
from .isEmpty import IsEmpty
from .lastAsync import LastAsync
from .max import Max
from .maxBy import MaxBy
from .min import Min
from .minBy import MinBy
from .select import Select
from .sequenceEqual import SequenceEqual
from .singleAsync import SingleAsync
from .sum import Sum
from .toDictionary import ToDictionary
from .toList import ToList

from rx.internal import defaultComparer, defaultCompareTo, identity
from rx.observable import Observable

def truePredicate(c): return True


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

def contains(self, value, equals=defaultComparer):
  assert isinstance(self, Observable)
  assert callable(equals)

  return Contains(self, value, equals)
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
