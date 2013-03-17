from rx.disposable import Disposable
from rx.observable import Producer
from .sink import Sink


class Generate(Producer):
  def __init__(self, initialState, condition, iterate, resultSelector, timeSelector, isAbsolute, scheduler):
    self.initialState = initialState
    self.condition = condition
    self.iterate = iterate
    self.resultSelector = resultSelector
    self.timeSelector = timeSelector
    self.isAbsolute = isAbsolute
    self.scheduler = scheduler

  def run(self, observer, cancel, setSink):
    if self.isAbsolute and self.timeSelector != None:
      sink = self.AlphaSink(self, observer, cancel)
      setSink(sink)
      return sink.run()
    elif not self.isAbsolute and self.timeSelector != None:
      sink = self.DeltaSink(self, observer, cancel)
      setSink(sink)
      return sink.run()
    else:
      sink = self.Sink(self, observer, cancel)
      setSink(sink)
      return sink.run()

  class AlphaSink(Sink):
    def __init__(self, parent, observer, cancel):
      super(Generate.AlphaSink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.first = True
      self.hasResult = False
      self.result = None

      return self.parent.scheduler.scheduleWithState(
        self.parent.initialState,
        self.invokeRec
      )

    def invokeRec(self, scheduler, state):
      time = 0

      if self.hasResult:
        self.observer.onNext(self.result)

      try:
        if self.first:
          self.first = False
        else:
          state = self.parent.iterate(state)

        self.hasResult = self.parent.condition(state)

        if self.hasResult:
          self.result = self.parent.resultSelector(state)
          time = self.parent.timeSelector(state)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
        return Disposable.empty()

      if not self.hasResult:
        self.observer.onCompleted()
        self.dispose()
        return Disposable.empty()

      return self.scheduleWithAbsoluteAndState(state, time, self.invokeRec)


  class DeltaSink(Sink):
    def __init__(self, parent, observer, cancel):
      super(Generate.DeltaSink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.first = True
      self.hasResult = False
      self.result = None

      return self.parent.scheduler.scheduleWithState(
        self.parent.initialState,
        self.invokeRec
      )

    def invokeRec(self, scheduler, state):
      time = 0

      if self.hasResult:
        self.observer.onNext(self.result)

      try:
        if self.first:
          self.first = False
        else:
          state = self.parent.iterate(state)

        self.hasResult = self.parent.condition(state)

        if self.hasResult:
          self.result = self.parent.resultSelector(state)
          time = self.parent.timeSelector(state)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
        return Disposable.empty()

      if not self.hasResult:
        self.observer.onCompleted()
        self.dispose()
        return Disposable.empty()

      return self.scheduleWithRelativeAndState(state, time, self.invokeRec)

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(Generate.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.state = self.parent.initialState
      self.first = True

      scheduler = self.parent.scheduler
      if scheduler.isLongRunning:
        return scheduler.scheduleLongRunning(self.loop)
      else:
        return scheduler.schedule(self.loopRec)

    def loop(self, cancel):
      while not cancel.isDisposed:
        hasResult = False
        result = None

        try:
          if self.first:
            self.first = False
          else:
            self.state = self.parent.iterate(self.state)

          hasResult = self.parent.condition(self.state)

          if hasResult:
            result = self.parent.resultSelector(self.state)
        except Exception as e:
          self.observer.onError(e)
          self.dispose()
          return

        if hasResult:
          self.observer.onNext(result)
        else:
          break

      if not cancel.isDisposed:
        self.observer.onCompleted()

      self.dispose()

    def loopRec(self, recurse):
      hasResult = False
      result = None

      try:
        if self.first:
          self.first = False
        else:
          self.state = self.parent.iterate(self.state)

        hasResult = self.parent.condition(self.state)

        if hasResult:
          result = self.parent.resultSelector(self.state)
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
        return

      if hasResult:
        self.observer.onNext(result)
        recurse()
      else:
        self.observer.onCompleted()
        self.dispose()
