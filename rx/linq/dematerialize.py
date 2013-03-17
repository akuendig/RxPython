from rx.observable import Producer
from rx.notification import Notification
from .sink import Sink


class Dematerialize(Producer):
  def __init__(self, source):
    self.source = source

  def run(self, observer, cancel, setSink):
    sink = self.Sink(observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, observer, cancel):
      super(Dematerialize.Sink, self).__init__(observer, cancel)

    def onNext(self, value):
      if value.kind == Notification.KIND_NEXT:
        self.observer.onNext(value.value)
      elif value.kind == Notification.KIND_ERROR:
        self.observer.onError(value.exception)
        self.dispose()
      elif value.kind == Notification.KIND_COMPLETED:
        self.observer.onCompleted()
        self.dispose()
      else:
        self.observer.onError(Exception("Unknown notification kind %s"%value.kind))

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()