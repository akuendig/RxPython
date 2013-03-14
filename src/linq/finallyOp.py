from disposable import Disposable
from observable import Producer
from .sink import Sink


class Finally(Producer):
  def __init__(self, source, action):
    self.source = source
    self.action = action

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(Finally.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      def dispose():
        try:
          subscription.dispose()
        finally:
          self.parent.action()

      subscription = self.parent.source.subscribeSafe(self)
      return Disposable.create(dispose)

    def onNext(self, value):
      self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()