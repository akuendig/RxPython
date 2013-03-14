from disposable import CompositeDisposable, Disposable
from observable import Observable, Producer
from .sink import Sink


class TimeStamp(Producer):
  def __init__(self, resourceFactory, observableFactory):
    self.resourceFactory = resourceFactory
    self.observableFactory = observableFactory

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(TimeStamp.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      source = None
      disposable = Disposable.empty()

      try:
        resource = self.parent.resourceFactory()
        if resource != None:
          disposable = resource

        source = self.parent.observableFactory(resource)
      except Exception as e:
        return CompositeDisposable(Observable.throw(e).subscribeSafe(self), disposable)

      return CompositeDisposable(source.subscribeSafe(self), disposable)

    def onNext(self, value):
      self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()