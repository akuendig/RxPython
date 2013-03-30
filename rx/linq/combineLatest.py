from rx.disposable import CompositeDisposable, SingleAssignmentDisposable
from rx.observable import Producer
from rx.observer import Observer
import rx.linq.sink
from threading import RLock


class CombineLatest(Producer):
  def __init__(self, sources, resultSelector):
    self.sources = sources
    self.resultSelector = resultSelector

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(CombineLatest.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      srcs = list(self.parent.sources)
      N = len(srcs)

      self.hasValue = [False]*N
      self.hasValueAll = False
      self.values = [None]*N
      self.isDone = [False]*N
      self.subscriptions = [None]*N

      self.gate = RLock()

      for i in range(N):
        d = SingleAssignmentDisposable()
        self.subscriptions[i] = d
        o = self.O(self, i)
        d.disposable = srcs[i].subscribeSafe(o)

      return CompositeDisposable(self.subscriptions)

    def onNext(self, index, value):
      with self.gate:
        self.values[index] = value
        self.hasValue[index] = True

        self.hasValueAll = self.hasValueAll or all(self.hasValue)

        if self.hasValueAll:
          res = None

          try:
            res = self.parent.resultSelector(self.values)
          except Exception as e:
            self.observer.onError(e)
            self.dispose()
            return

          self.observer.onNext(res)
        elif all(d for i, d in enumerate(self.isDone) if i != index):
          self.observer.onCompleted()
          self.dispose()
          return

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
          return
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