from observable import Producer
from observer import Observer
from concurrency import Atomic


class ForEach(Producer):
  class Sink(Observer):
    def __init__(self, onNext, done):
      self.onNextAction = onNext
      self.doneAction = done

      self.stopped = Atomic(False)
      self.exception = None

    def onNext(self, value):
      if not self.stopped.value:
        try:
          self.onNextAction(value)
        except Exception as e:
          self.onError(e)

    def onError(self, exception):
      if not self.stopped.exchange(True):
        self.exception = exception
        self.done()

    def onCompleted(self):
      if not self.stopped.exchange(True):
        self.done()

  class EnumeratingSink(Observer):
    def __init__(self, onNext, done):
      self.onNextAction = onNext
      self.doneAction = done

      self.index = 0
      self.stopped = Atomic(False)

    def onNext(self, value):
      if not self.stopped.value:
        try:
          self.onNextAction(value, self.index)
          self.index += 1
        except Exception as e:
          self.onError(e)

    def onError(self, exception):
      if not self.stopped.exchange(True):
        self.exception = exception
        self.done()

    def onCompleted(self):
      if not self.stopped.exchange(True):
        self.done()
