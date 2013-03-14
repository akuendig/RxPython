from disposable import CompositeDisposable
from observable import Producer
from observer import Observer
from .sink import Sink
from internal import defaultComparer
from collections import deque
from threading import RLock


class SequenceEqual(Producer):
  def __init__(self, first, second, equals=defaultComparer):
    self.first = first
    self.second = second
    self.equals = equals

  def run(self, observer, cancel, setSink):
    try:
      iter(self.second)
    except TypeError:
      sink = self.Sink(self, observer, cancel)
      setSink(sink)
      return self.source.subscribeSafe(sink)
    else:
      sink = self.IterableSink(self, observer, cancel)
      setSink(sink)
      return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(SequenceEqual.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.gate = RLock()
      self.donel = False
      self.doner = False
      self.ql = deque()
      self.qr = deque()

      return CompositeDisposable(
        self.parent.first.subscribeSafe(self.F(self)),
        self.parent.second.subscribeSafe(self.S(self))
      )

    class F(Observer):
      def __init__(self, parent):
        self.parent = parent

      def onNext(self, value):
        with self.parent.gate:
          if len(self.parent.qr) > 0:
            equal = False
            v = self.parent.qr.popleft()

            try:
              equal = self.parent.parent.equals(value, v)
            except Exception as e:
              self.parent.observer.onError(e)
              self.parent.dispose()
              return

            if not equal:
              self.parent.observer.onNext(False)
              self.parent.observer.onCompleted()
              self.parent.dispose()
          elif self.parent.doner:
            self.parent.observer.onNext(False)
            self.parent.observer.onCompleted()
            self.parent.dispose()
          else:
            self.parent.ql.append(value)

      def onError(self, exception):
        self.parent.observer.onError(exception)
        self.parent.dispose()

      def onCompleted(self):
        with self.parent.gate:
          self.parent.donel = True

          if len(self.parent.ql) == 0:
            if len(self.parent.qr) > 0:
              self.parent.observer.onNext(False)
              self.parent.observer.onCompleted()
              self.parent.dispose()
            elif self.parent.doner:
              self.parent.observer.onNext(True)
              self.parent.observer.onCompleted()
              self.parent.dispose()
    #end F

    class S(Observer):
      def __init__(self, parent):
        self.parent = parent

      def onNext(self, value):
        with self.parent.gate:
          if len(self.parent.ql) > 0:
            equal = False
            v = self.parent.ql.popleft()

            try:
              equal = self.parent.parent.equals(v, value)
            except Exception as e:
              self.parent.observer.onError(e)
              self.parent.dispose()
              return

            if not equal:
              self.parent.observer.onNext(False)
              self.parent.observer.onCompleted()
              self.parent.dispose()
          elif self.parent.donel:
            self.parent.observer.onNext(False)
            self.parent.observer.onCompleted()
            self.parent.dispose()
          else:
            self.parent.qr.append(value)

      def onError(self, exception):
        self.parent.observer.onError(exception)
        self.parent.dispose()

      def onCompleted(self):
        with self.parent.gate:
          self.parent.doner = True

          if len(self.parent.qr) == 0:
            if len(self.parent.ql) > 0:
              self.parent.observer.onNext(False)
              self.parent.observer.onCompleted()
              self.parent.dispose()
            elif self.parent.donel:
              self.parent.observer.onNext(True)
              self.parent.observer.onCompleted()
              self.parent.dispose()
    #end S
  #end Sink

  class IterableSink(Sink):
    def __init__(self, parent, observer, cancel):
      super(SequenceEqual.IterableSink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.iterator = iter(self.parent.second)

      return self.parent.first.subscribeSafe(self)

    def onNext(self, value):
      equal = False

      try:
        current = next(self.iterator)
        equal = self.parent.equals(value, current)
      except StopIteration:
        pass
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
        return

      if not equal:
        self.observer.onNext(False)
        self.observer.onCompleted()
        self.dispose()

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      hasNext = True

      try:
        next(self.iterator)
      except StopIteration:
        hasNext = False
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
        return

      self.observer.onNext(not hasNext)
      self.observer.onCompleted()
      self.dispose()

