from rx.disposable import Disposable, CompositeDisposable
from rx.observable import Producer, ConnectableObservable
from .sink import Sink


class Multicast(Producer):
  def __init__(self, source, subjectSelector, selector):
    self.source = source
    self.subjectSelector = subjectSelector
    self.selector = selector

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(Multicast.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      observable = None
      connectable = None

      try:
        subject = self.parent.subjectSelector()
        connectable = ConnectableObservable(self.parent.source, subject)
        observable = self.parent.selector(connectable)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
        return Disposable.empty()
      else:
        subscription = observable.subscribeSafe(self)
        connection = connectable.connect()

        return CompositeDisposable(subscription, connection)

    def onNext(self, value):
      self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()