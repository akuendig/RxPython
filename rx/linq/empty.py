from rx.observable import Producer
from .sink import Sink


class Empty(Producer):
  def __init__(self, scheduler):
    self.scheduler = scheduler

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(Empty.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      return self.parent.scheduler.schedule(self.invoke)

    def invoke(self):
      self.observer.onCompleted()
      self.dispose()