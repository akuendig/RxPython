from rx.notification import Notification
from rx.observable import PushToPullAdapter
from .sink import PushToPullSink
from threading import RLock, BoundedSemaphore


class Next(PushToPullAdapter):
  def __init__(self, source):
    super(Next, self).__init__(source)

  def run(self, subscription):
    return self.Sink(subscription)

  class Sink(PushToPullSink):
    def __init__(self, subscription):
      super(Next.Sink, self).__init__(subscription)
      self.gate = RLock()
      self.semaphore = BoundedSemaphore(1)
      self.semaphore.acquire()

      self.waiting = False
      self.kind = None
      self.value = None
      self.error = None

    def onNext(self, value):
      with self.gate:
        if self.waiting:
          self.value = value
          self.kind = Notification.KIND_NEXT
          self.semaphore.release()

        self.waiting = False

    def onError(self, exception):
      self.dispose()

      with self.gate:
        self.error = exception
        self.kind = Notification.KIND_ERROR

      if self.waiting:
        self.semaphore.release()

      self.waiting = False

    def onCompleted(self):
      self.dispose()

      with self.gate:
        self.kind = Notification.KIND_COMPLETED

      if self.waiting:
        self.semaphore.release()

      self.waiting = False

    def tryMoveNext(self):
      with self.gate:
        self.waiting = True
        done = self.kind != Notification.KIND_NEXT

      if not done:
        self.semaphore.acquire()
      #
      # When we reach this point, we released the lock and got the next notification
      # from the observer. We assume no concurrent calls to the TryMoveNext method
      # are made (per general guidance on usage of IEnumerable<T>). If the observer
      # enters the lock again, it should have quit it first, causing _waiting to be
      # set to false, hence future accesses of the lock won't set the _kind, _value,
      # and _error fields, until TryMoveNext is entered again and _waiting is reset
      # to true. In conclusion, the fields are stable for read below.
      #
      # Notice we rely on memory barrier acquire/release behavior due to the use of
      # the semaphore, not the lock (we're still under the lock when we release the
      # semaphore in the On* methods!).
      #
      kind = self.kind

      if kind == Notification.KIND_NEXT:
        self.current = self.value
        return True
      elif kind == Notification.KIND_ERROR:
        raise self.error
      elif kind == Notification.KIND_COMPLETED:
        pass
      else:
        self.observer.onError(Exception("Unknown notification kind %s"%kind))

      self.current = None
      return False