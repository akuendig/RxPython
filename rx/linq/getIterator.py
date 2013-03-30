from rx.disposable import SingleAssignmentDisposable
from rx.observer import Observer
import rx.linq.sink
from queue import Empty, Queue
from threading import Semaphore


class GetIterator(Observer):
  def __init__(self):
    self.queue = Queue()
    self.gate = Semaphore(0)
    self.subscription = SingleAssignmentDisposable()
    self.error = None
    self.done = False
    self.disposed = False

  def run(self, source):
    # [OK] Use of unsafe Subscribe: non-pretentious exact mirror with the dual GetEnumerator method.
    self.subscription.disposable = source.subscribe(self)
    return self

  def onNext(self, value):
    self.queue.put(value)
    self.gate.release()

  def onError(self, exception):
    self.error = exception
    self.subscription.dispose()
    self.gate.release()

  def onCompleted(self):
    self.done = True
    self.subscription.dispose()
    self.gate.release()

  def __iter__(self):
    return self

  def __next__(self):
    self.gate.acquire()

    if self.disposed:
      raise Exception("Object already disposed")

    try:
      return self.queue.get(True, 0)
    except Empty:
      pass

    if self.error != None:
      raise self.error

    assert self.done

    self.gate.release()

    raise StopIteration()

  def dispose(self):
    self.subscription.dispose()
    self.disposed = True
    self.gate.release()

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(GetIterator.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.currentKey = None
      self.hasCurrentKey = False

    def onNext(self, value):
      try:
        key = self.parent.keySelector(value)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
      else:
        equal = False

        if self.hasCurrentKey:
          try:
            equal = self.currentKey == key
          except Exception as e:
            self.observer.onError(e)
            self.dispose()

        if not self.hasCurrentKey or not equal:
          self.hasCurrentKey = True
          self.currentKey = key
          self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()