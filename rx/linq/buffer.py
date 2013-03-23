from rx.disposable import Disposable, CompositeDisposable, SingleAssignmentDisposable, SerialDisposable
from rx.internal import Struct
from rx.observable import Producer
from .sink import Sink
from threading import RLock
from collections import deque


class Buffer(Producer):
  def __init__(self, source, count=0, skip=0, timeSpan=0, timeShift=0, scheduler=None):
    if skip == 0:
      skip = count

    self.source = source
    self.count = count # length of each buffer
    self.skip = skip # number of elements to skip between creation of buffers
    self.timeShift = timeShift
    self.timeSpan = timeSpan
    self.scheduler = scheduler

  def run(self, observer, cancel, setSink):
    if self.scheduler == None:
      sink = self.SinkWithCount(self, observer, cancel)
      setSink(sink)
      return sink.run()
    elif self.count > 0:
      sink = self.SinkWithCountAndTimeSpan(self, observer, cancel)
      setSink(sink)
      return sink.run()
    else:
      if self.timeSpan == self.timeShift:
        sink = self.SinkWithTimeSpan(self, observer, cancel)
        setSink(sink)
        return sink.run()
      else:
        sink = self.SinkWithTimerAndTimeSpan(self, observer, cancel)
        setSink(sink)
        return sink.run()

  class SinkWithCount(Sink):
    def __init__(self, parent, observer, cancel):
      super(Buffer.SinkWithCount, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.queue = deque()
      self.n = 0

      self.createWindow()

      return self.parent.source.subscribeSafe(self)

    def createWindow(self):
      s = []
      self.queue.append(s)

    def onNext(self, value):
      for s in self.queue:
        s.append(value)

      c = self.n - self.parent.count + 1

      if c >= 0 and c % self.parent.skip == 0:
        s = self.queue.popleft()

        if len(s) > 0:
          self.observer.onNext(s)

      self.n += 1

      if self.n % self.parent.skip == 0:
        self.createWindow()

    def onError(self, exception):
      while len(self.queue) > 0:
        self.queue.popleft().clear()

      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      while len(self.queue) > 0:
        s = self.queue.popleft()

        if len(s) > 0:
          self.observer.onNext(s)

      self.observer.onCompleted()
      self.dispose()

  class SinkWithTimeSpan(Sink):
    def __init__(self, parent, observer, cancel):
      super(Buffer.SinkWithTimeSpan, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.gate = RLock()
      self.list = []

      d = self.parent.scheduler.schedulePeriodic(self.parent.timeSpan, self.tick)
      s = self.parent.source.subscribeSafe(self)

      return CompositeDisposable(d, s)

    def tick(self):
      with self.gate:
        self.observer.onNext(self.list)
        self.list = []

    def onNext(self, value):
      with self.gate:
        self.list.append(value)

    def onError(self, exception):
      with self.gate:
        self.list.clear()
        self.observer.onError(exception)
        self.dispose()

    def onCompleted(self):
      with self.gate:
        self.observer.onNext(self.list)
        self.observer.onCompleted()
        self.dispose()


  class SinkWithTimerAndTimeSpan(Sink):
    def __init__(self, parent, observer, cancel):
      super(Buffer.SinkWithTimerAndTimeSpan, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.totalTime = 0
      self.nextShift = self.parent.timeShift
      self.nextSpan = self.parent.timeSpan

      self.queue = deque()
      self.gate = RLock()

      self.timerDisposable = SerialDisposable()

      self.createWindow()
      self.createTimer()

      subscription = self.parent.source.subscribeSafe(self)

      return CompositeDisposable(self.timerDisposable, subscription)

    def createWindow(self):
      s = []
      self.queue.append(s)

    def createTimer(self):
      m = SingleAssignmentDisposable()
      self.timerDisposable.disposable = m

      isSpan = False
      isShift = False

      if self.nextSpan == self.nextShift:
        isSpan = True
        isShift = True
      elif self.nextShift < self.nextShift:
        isSpan = True
      else:
        isShift = True

      newTotalTime = self.nextSpan if isSpan else self.nextShift
      ts = newTotalTime - self.totalTime
      self.totalTime = newTotalTime

      if isSpan:
        self.nextSpan += self.parent.timeShift
      if isShift:
        self.nextShift += self.parent.timeShift

      m.disposable = self.parent.scheduler.scheduleWithRelativeAndState(
        Struct(isSpan=isSpan, isShift=isShift),
        ts,
        self.tick
      )

    def tick(self, scheduler, state):
      with self.gate:
        if state.isSpan:
          s = self.queue.popleft()
          self.observer.onNext(s)

        if state.isShift:
          self.createWindow()

      self.createTimer()

      return Disposable.empty()

    def onNext(self, value):
      with self.gate:
        for s in self.queue:
          s.append(value)

    def onError(self, exception):
      with self.gate:
        while len(self.queue) > 0:
          self.queue.popleft().clear()

        self.observer.onError(exception)
        self.dispose()

    def onCompleted(self):
      with self.gate:
        while len(self.queue) > 0:
          s = self.queue.popleft()
          self.observer.onNext(s)

        self.observer.onCompleted()
        self.dispose()

  class SinkWithCountAndTimeSpan(Sink):
    def __init__(self, parent, observer, cancel):
      super(Buffer.SinkWithCountAndTimeSpan, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.gate = RLock()
      self.list = []
      self.n = 0
      self.windowId = 0

      self.timerDisposable = SerialDisposable()
      self.createTimer(0)

      subscription = self.parent.source.subscribeSafe(self)

      return CompositeDisposable(self.timerDisposable, subscription)

    def createTimer(self, wId):
      m = SingleAssignmentDisposable()
      self.timerDisposable.disposable = m

      m.disposable = self.parent.schedule(
        wId,
        self.parent.timeSpan,
        self.tick
      )

    def tick(self, scheduler, wId):
      d = Disposable.empty()

      newId = 0

      with self.gate:
        if wId != self.windowId:
          return d

        self.n = 0
        self.windowId += 1
        newId = self.windowId

        res = self.list
        self.list = []
        self.observer.onNext(res)

      self.createTimer(newId)

      return d

    def onNext(self, value):
      newWindow = False
      newId = 0

      with self.gate:
        self.list.append(value)
        self.n += 1

        if self.n == self.parent.count:
          newWindow = True
          self.windowId += 1
          newId = self.windowId

          res = self.list
          self.list = []
          self.n = 0
          self.observer.onNext(res)

      if newWindow:
        self.createTimer(newId)

    def onError(self, exception):
      with self.gate:
        self.list.clear()
        self.observer.onError(exception)
        self.dispose()

    def onCompleted(self):
      with self.gate:
        self.observer.onNext(self.list)
        self.observer.onCompleted()
        self.dispose()