from observer import Observer
from concurrency import Atomic


class Sink(object):
  """Base class for implementation of query operators, providing
  a lightweight sink that can be disposed to mute the outgoing observer."""

  def __init__(self, observer, cancel):
    super(Sink, self).__init__()
    self.observer = observer
    self.cancel = Atomic(cancel)

  def dispose(self):
    self.observer = Observer.noop

    cancel = self.cancel.exchange(None)

    if cancel != None:
      cancel.dispose()

  class Forewarder(Observer):
    def __init__(self, foreward):
      self.foreward = foreward

    def onNext(self, value):
      self.foreward.observer.onNext(value)

    def onError(self, exception):
      self.foreward.observer.onError(exception)
      self.foreward.dispose()

    def onCompleted(self):
      self.foreward.observer.onCompleted()
      self.foreward.dispose()

  def getForewarder(self):
    return self.Forewarder(self)