from rx.observable import Producer
import rx.linq.sink


class Throw(Producer):
  def __init__(self, exception, scheduler):
    self.exception = exception
    self.scheduler = scheduler

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(Throw.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      return self.parent.scheduler.schedule(self.invoke)

    def invoke(self):
      self.observer.onError(self.parent.exception)
      self.dispose()
