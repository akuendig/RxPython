from rx.observable import Producer
from .sink import Sink


class Return(Producer):
  def __init__(self, value, scheduler):
    self.value = value
    self.scheduler = scheduler

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(Return.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      return self.parent.scheduler.schedule(self.invoke)

    def invoke(self):
      self.observer.onNext(self.parent.value)
      self.observer.onCompleted()
      self.dispose()