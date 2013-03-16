from observable import PushToPullAdapter
from .sink import PushToPullSink
from threading import RLock


class Collect(PushToPullAdapter):
  def __init__(self, source, getInitialCollector, merge, getNewCollector):
    self.source = source
    self.getInitialCollector = getInitialCollector
    self.merge = merge
    self.getNewCollector = getNewCollector

  def run(self, subscription):
    sink = self.Sink(self, subscription)
    return sink

  class Sink(PushToPullSink):
    def __init__(self, parent, subscription):
      super(Collect.Sink, self).__init__(subscription)
      self.parent = parent
      self.gate = RLock()
      self.collector = self.parent.getInitialCollector()
      self.hasFailed = False
      self.error = NotImplementedError
      self.hasCompleted = False
      self.done = False

    def onNext(self, value):
      with self.gate:
        try:
          self. collector = self.parent.merge(self.collector, value)
        except Exception as e:
          self.error = e
          self.hasFailed = True

          self.dispose()

    def onError(self, exception):
      self.dispose()

      with self.gate:
        self.error = exception
        self.hasFailed = True

    def onCompleted(self):
      self.dispose()

      with self.gate:
        self.hasCompleted = True

    def tryMoveNext(self):
      with self.gate:
        if self.hasFailed:
          self.current = None
          raise self.error
        else:
          if self.hasCompleted:
            if self.done:
              self.current = None
              return False

            self.current = self.collector
            self.done = True
          else:
            self.current = self.collector

            try:
              self.collector = self.parent.getNewCollector(self.current)
            except Exception as e:
              self.dispose()
              raise e

        return True

