from .observeOn import ObserveOn
from .synchronize import Synchronize

from rx.disposable import SchedulerDisposable, SerialDisposable, SingleAssignmentDisposable
from rx.observable import AnonymousObservable, Observable
from rx.scheduler import Scheduler


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