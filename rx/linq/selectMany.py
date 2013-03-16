from disposable import CompositeDisposable, SingleAssignmentDisposable
from observable import Producer
from observer import Observer
from .sink import Sink
from threading import RLock


## I intentionally left out the other implementation of SelectMany because it
## arises only because of requirements in C# LINQ


class SelectMany(Producer):
  def __init__(self, source, selector, selectorOnError, selectorOnCompleted, withIndex):
    self.source = source
    self.selector = selector
    self.selectorOnError = selectorOnError
    self.selectorOnCompleted = selectorOnCompleted
    self.withIndex = withIndex

  def run(self, observer, cancel, setSink):
    # if self.withIterableResult:
    #   sink = self.IterableSink(self, observer, cancel)
    #   setSink(sink)
    #   return sink.run()
    # else:
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(SelectMany.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.index = -1

    def run(self):
      self.gate = RLock()
      self.isStopped = False
      self.group = CompositeDisposable()

      self.sourceSubscription = SingleAssignmentDisposable()
      self.group.add(self.sourceSubscription)
      self.sourceSubscription.disposable = self.parent.source.subscribeSafe(self)

      return self.group

    def onNext(self, value):
      inner = None

      try:
        if self.parent.withIndex:
          self.index += 1
          inner = self.parent.selector(value, self.index)
        else:
          inner = self.parent.selector(value)
      except Exception as e:
        with self.gate:
          self.observer.onError(e)
          self.dispose()

      iterator = None

      try:
        iterator = iter(inner)
      except TypeError:
        # not iterable, assume observable
        self.subscribeInner(inner)
        return

      # iterable
      try:
        for current in iterator:
          self.observer.onNext(current)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()

    def onError(self, exception):
      if self.parent.selectorOnError != None:
        try:
          inner = None

          if self.parent.withIndex:
            self.index += 1
            inner = self.parent.selectorOnError(exception, self.index)
          else:
            inner = self.parent.selectorOnError(exception)
        except Exception as e:
          with self.gate:
            self.observer.onError(e)
            self.dispose()
        else:
          self.subscribeInner(inner)
          self.final()
      else:
        with self.gate:
          self.observer.onError(exception)
          self.dispose()

    def onCompleted(self):
      if self.parent.selectorOnCompleted != None:
        try:
          inner = None

          if self.parent.withIndex:
            inner = self.parent.selectorOnCompleted(self.index)
          else:
            inner = self.parent.selectorOnCompleted()
        except Exception as e:
          with self.gate:
            self.observer.onError(e)
            self.dispose()
            return
        else:
          self.subscribeInner(inner)

      self.final()

    def final(self):
      self.isStopped = True

      if self.group.length == 1:
        #
        # Notice there can be a race between OnCompleted of the source and any
        # of the inner sequences, where both see _group.Count == 1, and one is
        # waiting for the lock. There won't be a double OnCompleted observation
        # though, because the call to Dispose silences the observer by swapping
        # in a NopObserver<T>.
        #
        with self.gate:
          self.observer.onCompleted()
          self.dispose()
      else:
        self.sourceSubscription.dispose()

    def subscribeInner(self, inner):
      innerSubscription = SingleAssignmentDisposable()
      self.group.add(innerSubscription)
      innerSubscription.disposable = inner.subscribeSafe(self.LockingObserver(self, innerSubscription))

    class LockingObserver(Observer):
      def __init__(self, parent, subscription):
        self.parent = parent
        self.subscription = subscription

      def onNext(self, value):
        with self.parent.gate:
          self.parent.observer.onNext(value)

      def onError(self, exception):
        with self.parent.lock:
          self.parent.observer.onError(exception)
          self.parent.dispose()

      def onCompleted(self):
        self.parent.group.remove(self.subscription)

        if self.parent.isStopped and self.parent.group.length == 1:
          #
          # Notice there can be a race between OnCompleted of the source and any
          # of the inner sequences, where both see _group.Count == 1, and one is
          # waiting for the lock. There won't be a double OnCompleted observation
          # though, because the call to Dispose silences the observer by swapping
          # in a NopObserver<T>.
          #
          with self.parent.lock:
            self.parent.observer.onCompleted()
            self.parent.dispose()
    #end LockingObserver
  #end Sink

  # class IterableSink(Sink):
  #   def __init__(self, parent, observer, cancel):
  #     super(SelectMany.IterableSink, self).__init__(observer, cancel)
  #     self.parent = parent
  #     self.index = -1

