from observer import Observer
from concurrency import Atomic
from disposable import AsyncLock, Disposable, CompositeDisposable, SerialDisposable, SingleAssignmentDisposable
from scheduler import Scheduler


class Sink(object):
  """Base class for implementation of query operators, providing
  a lightweight sink that can be disposed to mute the outgoing observer."""

  def __init__(self, observer, cancel):
    super(Sink, self).__init__()
    self.observer = observer
    self.cancel = Atomic(cancel)

  def dispose(self):
    self.observer = Observer.noop

    cancel = self.cancel.exchange(None)

    if cancel != None:
      cancel.dispose()

  class Forewarder(Observer):
    def __init__(self, foreward):
      self.foreward = foreward

    def onNext(self, value):
      self.foreward.observer.onNext(value)

    def onError(self, exception):
      self.foreward.observer.onError(exception)
      self.foreward.dispose()

    def onCompleted(self):
      self.foreward.observer.onCompleted()
      self.foreward.dispose()

  def getForewarder(self):
    return self.Forewarder(self)


class TailRecursiveSink(Sink):
  def __init__(self, observer, cancel):
    super(TailRecursiveSink, self).__init__(observer, cancel)

  @staticmethod
  def unpack(source):
    while hasattr(source, 'eval'):
      source = source.eval()

    return source

  def run(self, sources):
    self.isDisposed = False
    self.subscription = SerialDisposable()
    self.gate = AsyncLock()
    self.stack = []
    self.length = []

    self.stack.append(iter(sources))
    self.length.append(len(sources))

    def scheduled(continuation):
      self.recurse = continuation
      self.gate.wait(self.moveNext)

    cancel = Scheduler.tailRecursion.scheduleRecursive(scheduled)

    return CompositeDisposable(
      self.subscription,
      cancel,
      Disposable.create(lambda: self.gate.wait(self.dispose))
    )

  def extract(self, source):
    raise NotImplementedError()

  def moveNext(self):
    hasCurrent = False
    current = None

    while True:
      if self.stack.count == 0:
        break

      if self.isDisposed:
        return

      e = self.stack[-1]
      l = self.length[-1]

      try:
        current = next(e)
        hasCurrent = True
      except StopIteration:
        pass
      except Exception as e:
        self.observer.onError(e)
        self.dispose()
        return

      if not hasCurrent:
        self.stack.pop()
        self.length.pop()
      else:
        r = l - 1
        self.length[-1] = r

        try:
          current = TailRecursiveSink.unpack(current)
        except Exception as e:
          self.observer.onError(e)
          self.dispose()
          return

        # Tail recursive case; drop the current frame.
        if r == 0:
          self.stack.pop()
          self.length.pop()

        # Flattening of nested sequences. Prevents stack overflow in observers.
        nextSeq = self.extract(current)

        if nextSeq != None:
          self.stack.append(iter(nextSeq))
          self.length.append(len(nextSeq))

          hasCurrent = False

      if hasCurrent:
        break

    if not hasCurrent:
      self.done()
      return

    d = SingleAssignmentDisposable()
    self.subscription.disposable = d
    d.disposable = current.subscribeSafe(self)

  def dispose(self):
    self.stack.clear()
    self.length.clear()
    self.isDisposed = True

  def done(self):
    self.observer.onCompleted()
    self.dispose()


class PushToPullSink(Observer):
  def __init__(self, subscription):
    super(PushToPullSink, self).__init__()
    self.subscription = subscription
    self.iteratorDone = False

  def tryMoveNext(self):
    raise NotImplementedError()

  def __next__(self):
    if not self.iteratorDone:
      if self.tryMoveNext():
        return self.current
      else:
        self.iteratorDone = True
        self.subscription.dispose()

    raise StopIteration()

  def dispose(self):
    self.subscription.dispose()


class ConcatSink(TailRecursiveSink):
  def __init__(self, observer, cancel):
    super(ConcatSink, self).__init__(observer, cancel)

  def extract(self, source):
    if hasattr(source, 'getSources'):
      return source.getSources()
    else:
      return None

  def onCompleted(self):
    self.recurse()

