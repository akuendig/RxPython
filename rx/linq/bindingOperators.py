from .multicast import Multicast
from .refCount import RefCount

from rx.observable import ConnectableObservable, Observable
from rx.scheduler import Scheduler
from rx.subject import AsyncSubject, BehaviorSubject, ReplaySubject, Subject

import sys


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
    return self.multicastIndividual(lambda: Subject(), selector)
  else:
    return self.multicastIndividual(lambda: BehaviorSubject(initialValue), selector)
Observable.publishIndividual = publishIndividual

def publishLast(self, selector=None):
  assert isinstance(self, Observable)

  if selector == None:
    return self.multicast(AsyncSubject())
  else:
    assert callable(selector)

    return self.multicastIndividual(lambda: AsyncSubject(), selector)
Observable.publishLast = publishLast

def refCount(self):
  assert isinstance(self, ConnectableObservable)

  return RefCount(self)
Observable.refCount = refCount

def replay(self, selector=None, bufferSize=sys.maxsize, window=sys.maxsize, scheduler=Scheduler.currentThread):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  if selector == None:
    return self.multicast(ReplaySubject(bufferSize, window, scheduler))
  else:
    assert callable(selector)

    return self.multicastIndividual(lambda: ReplaySubject(bufferSize, window, scheduler), selector)
Observable.replay = replay
