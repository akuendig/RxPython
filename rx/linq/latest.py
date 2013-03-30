from rx.notification import Notification
from rx.observable import PushToPullAdapter
import rx.linq.sink
from threading import RLock, BoundedSemaphore


class Latest(PushToPullAdapter):
  def __init__(self, source):
    super(Latest, self).__init__(source)

  def run(self, subscription):
    return self.Sink(subscription)

  class Sink(rx.linq.sink.PushToPullSink):
    def __init__(self, subscription):
      super(Latest.Sink, self).__init__(subscription)
      self.gate = RLock()
      self.semaphore = BoundedSemaphore(1)
      self.semaphore.acquire()

      self.notificationAvailable = False
      self.kind = None
      self.value = None
      self.error = None

    def onNext(self, value):
      lackedValue = False

      with self.gate:
        lackedValue = not self.notificationAvailable
        self.notificationAvailable = True
        self.kind = Notification.KIND_NEXT
        self.value = value

      if lackedValue:
        self.semaphore.release()

    def onError(self, exception):
      self.dispose()
      lackedValue = False

      with self.gate:
        lackedValue = not self.notificationAvailable
        self.notificationAvailable = True
        self.kind = Notification.KIND_ERROR
        self.error = exception

      if lackedValue:
        self.semaphore.release()

    def onCompleted(self):
      self.dispose()
      lackedValue = False

      with self.gate:
        lackedValue = not self.notificationAvailable
        self.notificationAvailable = True
        self.kind = Notification.KIND_COMPLETED

      if lackedValue:
        self.semaphore.release()

    def tryMoveNext(self):
      kind = None
      value = None
      error = None

      self.semaphore.acquire()

      with self.gate:
        kind = self.kind

        if kind == Notification.KIND_NEXT:
          value = self.value
        elif kind == Notification.KIND_ERROR:
          error = self.error

        self.notificationAvailable = False

      if kind == Notification.KIND_NEXT:
        self.current = value
        return True
      elif kind == Notification.KIND_ERROR:
        raise error
      elif kind == Notification.KIND_COMPLETED:
        pass
      else:
        self.observer.onError(Exception("Unknown notification kind %s"%kind))

      self.current = None
      return False