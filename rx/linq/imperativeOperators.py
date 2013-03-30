from .case import Case
from .doWhile import DoWhile
from .forOp import For
from .ifOp import If
from .whileOp import While

from rx.observable import Observable
from rx.scheduler import Scheduler

import collections


####################
#    Imperative    #
####################

def case(selector, sources, schedulerOrDefaultSource=None):
  assert callable(selector)
  assert isinstance(sources, dict)

  if schedulerOrDefaultSource == None:
    return Case(selector, sources, Observable.empty())
  elif isinstance(schedulerOrDefaultSource, Scheduler):
    return Case(selector, sources, Observable.empty(schedulerOrDefaultSource))
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
    return If(condition, thenSource, Observable.empty())
  elif isinstance(schedulerOrElseSource, Scheduler):
    return If(condition, thenSource, Observable.empty(schedulerOrElseSource))
  else:
    assert isinstance(schedulerOrElseSource, Observable)

    return If(condition, thenSource, schedulerOrElseSource)
Observable.branch = branch

def loop(source, condition):
  assert isinstance(source, Observable)
  assert callable(condition)

  return While(source, condition)
Observable.loop = loop