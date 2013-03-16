from notification import Notification
from observable import Producer
from .sink import Sink


class Materialize(Producer):
  def __init__(self, source):
    self.source = source

  def dematerialize(self):
    return self.source.asObservable()

  def run(self, observer, cancel, setSink):
    sink = self.Sink(observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, observer, cancel):
      super(Materialize.Sink, self).__init__(observer, cancel)

    def onNext(self, value):
      self.observer.onNext(Notification.createOnNext(value))

    def onError(self, exception):
      self.observer.onNext(Notification.createOnError(exception))
      self.observer.onCompleted()
      self.dispose()

    def onCompleted(self):
      self.observer.onNext(Notification.createOnCompleted())
      self.observer.onCompleted()
      self.dispose()