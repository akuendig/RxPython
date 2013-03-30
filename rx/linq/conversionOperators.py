from .toObservable import ToObservable

from rx.observable import Observable
from rx.scheduler import Scheduler


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