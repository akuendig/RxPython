from rx.disposable import SerialDisposable, SingleAssignmentDisposable
from rx.observable import Producer
from rx.observer import Observer
import rx.linq.sink


class CatchFallback(Producer):
  def __init__(self, sources):
    self.sources = sources

  def run(self, observer, cancel, setSink):
    sink = self.Sink(observer, cancel)
    setSink(sink)
    return sink.run(self.sources)

  class Sink(rx.linq.sink.TailRecursiveSink):
    def __init__(self, observer, cancel):
      super(CatchFallback.Sink, self).__init__(observer, cancel)
      self.lastException = None

    def extract(self, source):
      if isinstance(source, CatchFallback):
        return source.sources

      return None

    def onNext(self, value):
      self.observer.onNext(value)

    def onError(self, exception):
      self.lastException = exception
      self.recurse()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()

    def done(self):
      if self.lastException != None:
        self.observer.onError(self.lastException)
      else:
        self.observer.onCompleted()

      self.dispose()


class CatchException(Producer):
  def __init__(self, source, handler, exceptionType):
    self.source = source
    self.handler = handler
    self.exceptionType = exceptionType

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(CatchException.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.subscription = SerialDisposable()

      d = SingleAssignmentDisposable()
      self.subscription.disposable = d
      d.disposable = self.parent.source.subscribeSafe(self)

      return self.subscription

    def onNext(self, value):
      self.observer.onNext(value)

    def onError(self, exception):
      if isinstance(exception, self.parent.exceptionType):
        result = None

        try:
          result = self.parent.handler(exception)
        except Exception as e:
          self.observer.onError(e)
          self.dispose()
          return

        d = SingleAssignmentDisposable()
        self.subscription.disposable = d
        d.disposable = result.subscribeSafe(CatchException.WrapObserver(self))
      else:
        self.observer.onError(exception)
        self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()

  class WrapObserver(Observer):
    def __init__(self, parent):
      super(CatchException.WrapObserver, self).__init__()
      self.parent = parent

    def onNext(self, value):
      self.parent.observer.onNext(value)

    def onError(self, exception):
      self.parent.observer.onError(exception)
      self.parent.dispose()

    def onCompleted(self):
      self.parent.observer.onCompleted()
      self.parent.dispose()


