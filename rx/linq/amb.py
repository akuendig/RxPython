from rx.observer import Observer
from rx.observable import Producer
from rx.disposable import CompositeDisposable, SingleAssignmentDisposable
import rx.linq.sink
from threading import RLock


class Amb(Producer):
  LEFT = 0
  RIGHT = 1
  NEITHER = 2

  def __init__(self, left, right):
    self.left = left
    self.right = right

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class DecisionObserver(Observer):
    def __init__(self, parent, gate, me, subscription, otherSubscription, observer):
      super(Amb.DecisionObserver, self).__init__()
      self.parent = parent
      self.gate = gate
      self.me = me
      self.subscription = subscription
      self.otherSubscription = otherSubscription
      self.observer = observer

    def onNext(self, value):
      with self.gate:
        if self.parent.choice == Amb.NEITHER:
          self.parent.choice = self.me
          self.otherSubscription.dispose()
          self.observer.disposable = self.subscription
          self.observer.target = self.parent.observer

        if self.parent.choice == self.me:
          self.parent.observer.onNext(value)

    def onError(self, exception):
      with self.gate:
        if self.parent.choice == Amb.NEITHER:
          self.parent.choice = self.me
          self.otherSubscription.dispose()
          self.observer.disposable = self.subscription
          self.observer.target = self.parent.observer

        if self.parent.choice == self.me:
          self.parent.observer.onError(exception)
          self.parent.dispose()

    def onCompleted(self):
      with self.gate:
        if self.parent.choice == Amb.NEITHER:
          self.parent.choice = self.me
          self.otherSubscription.dispose()
          self.observer.disposable = self.subscription
          self.observer.target = self.parent.observer

        if self.parent.choice == self.me:
          self.parent.observer.onCompleted()
          self.parent.dispose()
  #end DecisionObserver

  class AmbObserver(Observer):
    def __init__(self, target):
      super(Amb.AmbObserver, self).__init__()
      self.target = target

    def onNext(self, value):
      self.target.onNext(value)

    def onError(self, exception):
      self.target.onError(exception)
      self.disposable.dispose()

    def onCompleted(self):
      self.target.onCompleted()
      self.disposable.dispose()
  #end AmbObserver

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(Amb.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      ls = SingleAssignmentDisposable()
      rs = SingleAssignmentDisposable()

      d = CompositeDisposable(ls, rs)

      gate = RLock()

      lo = Amb.AmbObserver(self)
      lo.disposable = d
      lo.target = Amb.DecisionObserver(self, gate, Amb.LEFT, ls, rs, lo)

      ro = Amb.AmbObserver(self)
      ro.disposable = d
      ro.target = Amb.DecisionObserver(self, gate, Amb.RIGHT, rs, ls, ro)

      self.choice = Amb.NEITHER

      ls.disposable = self.parent.left.subscribeSafe(lo)
      rs.disposable = self.parent.right.subscribeSafe(ro)

      return d

    def onNext(self, value):
      res = False

      try:
        res = self.parent.predicate(value)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
        return

      if not res:
        self.observer.onNext(False)
        self.observer.onCompleted()
        self.dispose()

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onNext(True)
      self.observer.onCompleted()
      self.dispose()
  #end Sink
#end Amb