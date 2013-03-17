from rx.disposable import Disposable, SingleAssignmentDisposable
from rx.observable import Producer
from rx.subject import Subject
from threading import RLock

class EventProducer(Producer):
  def __init__(self, scheduler):
    self.scheduler = scheduler
    self.gate = RLock()
    self.session = None

  def getHandler(self, onNext):
    raise NotImplementedError()

  def addHandler(self, handler):
    raise NotImplementedError()

  def run(self, observer, cancel, setSink):
    connection = None

    with self.gate:
      #
      # A session object holds on to a single handler to the underlying event, feeding
      # into a subject. It also ref counts the number of connections to the subject.
      #
      # When the ref count goes back to zero, the event handler is unregistered, and
      # the session will reach out to reset the _session field to null under the _gate
      # lock. Future subscriptions will cause a new session to be created.
      #
      if self.session == None:
        self.session = self.Session(self)

      connection = self.session.connect(observer)

    return connection

  class Session(object):
    def __init__(self, parent):
      self.parent = parent
      self.removeHandler = None
      self.subject = Subject()
      self.count = 0

    def connect(self, observer):
      #
      # We connect the given observer to the subject first, before performing any kind
      # of initialization which will register an event handler. This is done to ensure
      # we don't have a time gap between adding the handler and connecting the user's
      # subject, e.g. when the ImmediateScheduler is used.
      #
      # [OK] Use of unsafe Subscribe: called on a known subject implementation.
      #
      connection = self.subject.subscribe(observer)

      self.count += 1
      if self.count == 1:
        try:
          self.initialize()
        except Exception as e:
          self.count -= 1
          connection.dispose()

          observer.onErro(e)
          return Disposable.empty()

      def dispose():
        connection.dispose()

        with self.parent.gate:
          self.count -=1
          if self.count == 0:
            self.parent.scheduler.schedule(self.removeHandler.dispose)
            self.parent.session = None

      return Disposable.create(dispose)

    def initialize(self):
      #
      # When the ref count goes to zero, no-one should be able to perform operations on
      # the session object anymore, because it gets nulled out.
      #
      assert self.removeHandler == None
      self.removeHandler = SingleAssignmentDisposable()

      #
      # Conversion code is supposed to be a pure function and shouldn't be run on the
      # scheduler, but the add handler call should. Notice the scheduler can be the
      # ImmediateScheduler, causing synchronous invocation. This is the default when
      # no SynchronizationContext is found (see QueryLanguage.Events.cs and search for
      # the GetSchedulerForCurrentContext method).
      #

      onNext = self.parent.getHandler(self.subject.onNext)
      self.parent.scheduler.scheduleWithState(onNext, self.addHandler)

    def addHandler(self, scheduler, onNext):
      try:
        removeHandler = self.parent.addHandler(onNext)
      except Exception as e:
        self.subject.onError(e)
      else:
        self.removeHandler.disposable = removeHandler

      #
      # We don't propagate the exception to the OnError channel upon Dispose. This is
      # not possible at this stage, because we've already auto-detached in the base
      # class Producer implementation. Even if we would switch the OnError and auto-
      # detach calls, it wouldn't work because the remove handler logic is scheduled
      # on the given scheduler, causing asynchrony. We can't block waiting for the
      # remove handler to run on the scheduler.
      #
      return Disposable.empty()
  #end Session

class ClassicEventProducer(EventProducer):
  def __init__(self, addHandler, removeHandler, scheduler):
    super(ClassicEventProducer, self).__init__(scheduler)
    self.addHandlerAction = addHandler
    self.removeHandlerAction = removeHandler

  def addHandler(self, handler):
    self.addHandlerAction(handler)
    return Disposable.create(lambda: self.removeHandlerAction(handler))


class FromEvent(ClassicEventProducer):
  def __init__(self, addHandler, removeHandler, scheduler):
    super(FromEvent, self).__init__(addHandler, removeHandler, scheduler)

  def getHandler(self, onNext):
    return onNext

