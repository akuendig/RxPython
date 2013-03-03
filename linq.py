from observer import Observer
from observable import Producer
from disposable import CompositeDisposable, SingleAssignmentDisposable
from concurrency import Atomic
from threading import RLock

class Sink(object):
  """Base class for implementation of query operators, providing
  a lightweight sink that can be disposed to mute the outgoing observer."""

  def __init__(self, observer, cancel):
    super(Sink, self).__init__()
    self.observer = observer
    self.cancel = Atomic(cancel)

  def dispose(self):
    self.observer = Observer.noop

    cancel = self.cancel.exchange(None)

    if cancel != None:
      cancel.dispose()

  class Forewarder(Observer):
    def __init__(self, foreward):
      self.foreward = foreward

    def onNext(self, value):
      self.foreward.observer.onNext(value)

    def onError(self, exception):
      self.foreward.observer.onError(exception)
      self.foreward.dispose()

    def onCompleted(self):
      self.foreward.observer.onCompleted()
      self.foreward.dispose()

  def getForewarder(self):
    return self.Forewarder(self)


class AddRef(Producer):
  def __init__(self, source, refCount):
    self.source = source
    self.refCount = refCount

  def run(self, observer, cancel, setSink):
    d = CompositeDisposable(self.refCount.getDisposable(), cancel)

    sink = Sink(observer, d)
    setSink(sink)

    return self.source.subscribeSafe(sink)


class Aggregate(Producer):
  def __init__(self, source, seed, accumulator, resultSelector = id):
    self.source = source
    self.seed = seed
    self.accumulator = accumulator
    self.resultSelector = resultSelector

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(Aggregate.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.accumulation = parent.seed

    def onNext(self, value):
      try:
        self.accumulation = self.parent.accumulator(self.accumulation, value)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      result = None

      try:
        result = self.parent.resultSelector(self.accumulation)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
        return

      self.observer.onNext(result)
      self.observer.onCompleted()
      self.dispose()


class All(Producer):
  def __init__(self, source, predicate):
    self.source = source
    self.predicate = predicate

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(All.Sink, self).__init__(observer, cancel)
      self.parent = parent

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

  class AmbObserver(Observer):
    def onNext(self, value):
      self.target.onNext(value)

    def onError(self, exception):
      self.target.onError(exception)
      self.disposable.dispose()

    def onCompleted(self):
      self.target.onCompleted()
      self.disposable.dispose()

  class DecisionObserver(Observer):
    def __init__(self, parent, gate, me, subscription, otherSubscription, observer):
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

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(Amb.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      ls = SingleAssignmentDisposable()
      rs = SingleAssignmentDisposable()

      d = CompositeDisposable(ls, rs)

      gate = RLock()

      lo = self.AmbObserver()
      lo.disposable = d
      lo.target = self.DecisionObserver(self, gate, Amb.LEFT, ls, rs, lo)

      ro = self.AmbObserver()
      ro.disposable = d
      ro.target = self.DecisionObserver(self, gate, Amb.RIGHT, rs, ls, ro)

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


class Any(Producer):
  def __init__(self, source, predicate=lambda _: True):
    self.source = source
    self.predicate = predicate

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(Any.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def onNext(self, value):
      res = False

      try:
        res = self.parent.predicate(value)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
        return

      if res:
        self.observer.onNext(True)
        self.observer.onCompleted()
        self.dispose()

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onNext(False)
      self.observer.onCompleted()
      self.dispose()


class AsObservable(Producer):
  def __init__(self, source, predicate=lambda _: True):
    self.source = source
    self.predicate = predicate

  def omega(self):
    return self

  def eval(self):
    return self.source

  def run(self, observer, cancel, setSink):
    sink = self.Sink(observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, observer, cancel):
      super(AsObservable.Sink, self).__init__(observer, cancel)

    def onNext(self, value):
      self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()


class Average(Producer):
  def __init__(self, source, selector=id):
    self.source = source
    self.selector = selector

  def run(self, observer, cancel, setSink):
    sink = self.Sink(observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, observer, cancel):
      super(Average.Sink, self).__init__(observer, cancel)
      self.sum = 0
      self.count = 0

    def onNext(self, value):
      try:
        self.sum += value
        self.count += 1
      except Exception as e:
        self.observer.onError(e)
        self.dispose()

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      try:
        self.observer.onNext(self.sum / self.count)
        self.observer.onCompleted()
      except Exception as e:
        self.observer.onError(e)
      finally:
        self.dispose()
