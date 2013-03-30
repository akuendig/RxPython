from .buffer import Buffer
from .delay import DelayObservable, DelaySubscription, DelayTime
from .generate import Generate
from .sample import SampleWithObservable, SampleWithTime
from .throttle import ThrottleObservable, ThrottleTime
from .timeInterval import TimeInterval
from .timeout import TimeoutAbsolute, TimeoutRelative, TimeoutObservable
from .timer import Timer
from .timestamp import TimeStamp
from .window import Window

from rx.observable import Observable
from rx.scheduler import Scheduler


####################
#       Time       #
####################

def bufferWithTime(self, timeSpan, timeShift=None, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  if timeShift == None:
    timeShift = timeSpan
  return Buffer(self, timeSpan=timeSpan, timeShift=timeShift, scheduler=scheduler)
Observable.bufferWithTime = bufferWithTime

def bufferWithTimeAndCount(self, timeSpan, count=None, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  if count == None:
    count = timeSpan
  return Buffer(self, timeSpan=timeSpan, count=count, scheduler=scheduler)
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

def delayIndividual(self, delayDurationSelector, subscriptionDelayObservable=None):
  assert isinstance(self, Observable)
  assert callable(delayDurationSelector)

  if subscriptionDelayObservable != None:
    assert isinstance(subscriptionDelayObservable, Observable)

  return DelayObservable(self, subscriptionDelayObservable, delayDurationSelector)
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

  return Timer(period, False, period, scheduler)
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

def timeoutIndividual(self, durationSelector, firstTimeout=None, other=None):
  assert isinstance(self, Observable)

  if firstTimeout == None:
    firstTimeout = Observable.never()
  if other == None:
    other = Observable.throw(Exception("Timeout in observable"))

  assert isinstance(firstTimeout, Observable)
  assert isinstance(other, Observable)

  return TimeoutObservable(self, firstTimeout, durationSelector, other)
Observable.timeoutIndividual = timeoutIndividual

def timerRelative(dueTime, period=None, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(scheduler, Scheduler)

  return Timer(dueTime, False, period, scheduler)
Observable.timerRelative = timerRelative

def timerAbsolute(dueTime, period=None, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(scheduler, Scheduler)

  return Timer(dueTime, True, period, scheduler)
Observable.timerAbsolute = timerAbsolute

def timestamp(self, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  return TimeStamp(self, scheduler)
Observable.timestamp = timestamp

def windowWithTime(self, timeSpan, timeShift=None, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  if timeShift == None:
    timeShift = timeSpan
  return Window(self, timeSpan=timeSpan, timeShift=timeShift, scheduler=scheduler)
Observable.windowWithTime = windowWithTime

def windowWithTimeAndCount(self, timeSpan, count=None, scheduler=Scheduler.timeBasedOperation):
  assert isinstance(self, Observable)
  assert isinstance(scheduler, Scheduler)

  if count == None:
    count = timeSpan
  return Window(self, timeSpan=timeSpan, count=count, scheduler=scheduler)
Observable.windowWithTimeAndCount = windowWithTimeAndCount
