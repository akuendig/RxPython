from rx.disposable import CompositeDisposable, Disposable, SingleAssignmentDisposable
from rx.observable import Producer
from rx.observer import Observer
import rx.linq.sink
from collections import deque
from threading import RLock


class Zip(Producer):
  def __init__(self, sources):
    self.sources = sources

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(Zip.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      srcs = list(self.parent.sources)

      N = len(srcs)

      self.queues = [None] * N
      self.isDone = [False] * N
      self.subscriptions = [None] * N
      self.gate = RLock()

      for i in range(0, N):
        self.queues[i] = deque()

      # Loop twice because subscribing could already yield
      # a value before all queues are initialized
      for i in range(0, N):
        d = SingleAssignmentDisposable()
        self.subscriptions[i] = d

        o = self.O(self, i)
        d.disposable = srcs[i].subscribeSafe(o)

      c = CompositeDisposable(self.subscriptions)

      def dispose():
        for q in self.queues:
          q.clear()

      c.add(Disposable.create(dispose))

      return c

    def onNext(self, index, value):
      with self.gate:
        self.queues[index].append(value)

        if all([len(q) > 0 for q in self.queues]):
          res = tuple(map(lambda q: q.popleft(), self.queues))
          self.observer.onNext(res)
        elif all(d for i, d in enumerate(self.isDone) if i != index):
          self.observer.onCompleted()
          self.dispose()

    def onError(self, exception):
      with self.gate:
        self.observer.onError(exception)
        self.dispose()

    def onCompleted(self, index):
      with self.gate:
        self.isDone[index] = True

        if all(self.isDone):
          self.observer.onCompleted()
          self.dispose()
        else:
          self.subscriptions[index].dispose()

    class O(Observer):
      def __init__(self, parent, index):
        self.parent = parent
        self.index = index

      def onNext(self, value):
        self.parent.onNext(self.index, value)

      def onError(self, exception):
        self.parent.onError(exception)

      def onCompleted(self):
        self.parent.onCompleted(self.index)
