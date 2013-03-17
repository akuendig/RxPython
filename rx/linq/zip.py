from rx.disposable import CompositeDisposable, Disposable, SingleAssignmentDisposable
from rx.observable import Producer
from rx.observer import Observer
from .sink import Sink
from collections import deque
from itertools import repeat
from threading import RLock


class Zip(Producer):
  def __init__(self, sources):
    self.sources = sources

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(Zip.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      srcs = list(self.parent.sources)

      N = len(srcs)

      self.queues = list(repeat(None, N))
      self.isDone = list(repeat(False, N))
      self.subscriptions = list(repeat(None, N))
      self.gate = RLock()

      for i in range(0, N):
        self.queues[i] = deque()

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

        if all(map(lambda q: len(q) > 0)):
          res = list(map(lambda q: q.popleft()))
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
