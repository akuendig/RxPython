from rx.observable import Producer
from rx.observer import ObserveOnObserver


class ObserveOn(Producer):
  def __init__(self, source, scheduler):
    self.source = source
    self.scheduler = scheduler

  def run(self, observer, cancel, setSink):
    sink = ObserveOnObserver(self.scheduler, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)