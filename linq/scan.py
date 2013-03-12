from observable import Producer
from .sink import Sink


class ScanWithSeed(Producer):
  def __init__(self, source, seed, accumulator):
    self.source = source
    self.seed = seed
    self.accumulator = accumulator

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(ScanWithSeed.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.accumulation = None
      self.hasAccumulation = False

    def onNext(self, value):
      try:
        if self.hasAccumulation:
          self.accumulation = self.parent.accumulator(self.accumulation, value)
        else:
          self.accumulation = self.parent.accumulator(self.parent.seed, value)
          self.hasAccumulation = True
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
      else:
        self.observer.onNext(self.accumulation)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()


class ScanWithoutSeed(Producer):
  def __init__(self, source, accumulator):
    self.source = source
    self.accumulator = accumulator

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(ScanWithoutSeed.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.accumulation = None
      self.hasAccumulation = False

    def onNext(self, value):
      try:
        if self.hasAccumulation:
          self.accumulation = self.parent.accumulator(self.accumulation, value)
        else:
          self.accumulation = value
          self.hasAccumulation = True
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
      else:
        self.observer.onNext(self.accumulation)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()