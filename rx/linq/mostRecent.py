from rx.notification import Notification
from rx.observable import PushToPullAdapter
import rx.linq.sink


class MostRecent(PushToPullAdapter):
  def __init__(self, source):
    super(MostRecent, self).__init__(source)

  def run(self, subscription):
    return self.Sink(subscription)

  class Sink(rx.linq.sink.PushToPullSink):
    def __init__(self, subscription):
      super(MostRecent.Sink, self).__init__(subscription)
      self.kind = None
      self.value = None
      self.error = None

    def onNext(self, value):
      self.value = value
      self.kind = Notification.KIND_NEXT

    def onError(self, exception):
      self.dispose()

      self.error = exception
      self.kind = Notification.KIND_ERROR

    def onCompleted(self):
      self.dispose()

      self.kind = Notification.KIND_COMPLETED

    def tryMoveNext(self):
      kind = self.kind

      if kind == Notification.KIND_NEXT:
        self.current = self.value
        return True
      elif kind == Notification.KIND_ERROR:
        raise self.error
      elif kind == Notification.KIND_COMPLETED:
        pass
      else:
        self.observer.onError(Exception("Unknown notification kind %s"%self.kind))

      self.current = None
      return False