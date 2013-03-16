from disposable import CompositeDisposable, SingleAssignmentDisposable
from observable import Producer
from observer import Observer
from .sink import Sink
from threading import RLock
from queue import Queue


class Merge(Producer):
  def __init__(self, sources, maxConcurrency):
    self.sources = sources
    self.maxConcurrency = maxConcurrency

  def run(self, observer, cancel, setSink):
    if self.maxConcurrency > 0:
      sink = self.ConcurrentSink(self, observer, cancel)
      setSink(sink)
      return sink.run()
    else:
      sink = self.SerialSink(self, observer, cancel)
      setSink(sink)
      return sink.run()

  class SerialSink(Sink):
    def __init__(self, parent, observer, cancel):
      super(Merge.SerialSink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.gate = RLock()
      self.isStopped = False
      self.group = CompositeDisposable()

      self.sourceSubscription = SingleAssignmentDisposable()
      self.group.add(self.sourceSubscription)
      self.sourceSubscription.disposable = self.parent.sources.subscribeSafe(self)

      return self.group

    def onNext(self, value):
      innerSubscription = SingleAssignmentDisposable()
      self.group.add(innerSubscription)
      innerSubscription.disposable = value.subscribeSafe(self.LockObserver(self, innerSubscription))

    def onError(self, exception):
      with self.gate:
        self.observer.onError(exception)
        self.dispose()

    def onCompleted(self):
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

    class LockObserver(Observer):
      def __init__(self, parent, subscription):
        self.parent = parent
        self.subscription = subscription

      def onNext(self, value):
        with self.parent.gate:
          self.parent.observer.onNext(value)

      def onError(self, exception):
        with self.parent.gate:
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
          with self.parent.gate:
            self.parent.observer.onCompleted()
            self.parent.dispose()


  class ConcurrentSink(Sink):
    def __init__(self, parent, observer, cancel):
      super(Merge.ConcurrentSink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.gate = RLock()
      self.q = Queue()
      self.isStopped = False
      self.activeCount = 0

      self.group = CompositeDisposable()
      self.sourceSubscription = SingleAssignmentDisposable()
      self.group.add(self.sourceSubscription)
      self.sourceSubscription.disposable = self.parent.sources.subscribeSafe(self)

      return self.group

    def onNext(self, value):
      with self.gate:
        if self.activeCount < self.parent.maxConcurrency:
          self.activeCount += 1
          self.subscribe(value)
        else:
          self.q.put_nowait(value)

    def onError(self, exception):
      with self.gate:
        self.observer.onError(exception)
        self.dispose()

    def onCompleted(self):
      with self.gate:
        self.isStopped = True

        if self.activeCount == 0:
          self.observer.onCompleted()
          self.dispose()
        else:
          self.sourceSubscription.dispose()

    def subscribe(self, innerSource):
      subscription = SingleAssignmentDisposable()
      self.group.add(subscription)
      subscription.disposable = innerSource.subscribeSafe(self.LockObserver(self, subscription))

    class LockObserver(Observer):
      def __init__(self, parent, subscription):
        self.parent = parent
        self.subscription = subscription

      def onNext(self, value):
        with self.parent.gate:
          self.parent.observer.onNext(value)

      def onError(self, exception):
        with self.parent.gate:
          self.parent.observer.onError(exception)
          self.parent.dispose()

      def onCompleted(self):
        self.parent.group.remove(self.subscription)

        with self.parent.gate:
          if self.parent.q.qsize() > 0:
            s = self.q.get()
            self.parent.subscribe(s)
          else:
            self.parent.activeCount -= 1

            if self.parent.isStopped and self.parent.activeCount == 0:
              self.parent.observer.onCompleted()
              self.parent.dispose()