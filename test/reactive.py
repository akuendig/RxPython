import unittest

from rx.disposable import Disposable
from rx.internal import Struct
from rx.notification import Notification
from rx.observable import Observable
from rx.observer import Observer
from rx.scheduler import HistoricalScheduler


def OnNext(value):
  return Notification.createOnNext(value)

def OnError(exception):
  return Notification.createOnError(exception)

def OnCompleted():
  return Notification.createOnCompleted()

class TestScheduler(HistoricalScheduler):
  TIME_CREATE = 100
  TIME_SUBSCRIBE = 200
  TIME_DISPOSE = 1000

  def __init__(self):
    super(TestScheduler, self).__init__()

  def createObserver(self):
    return self.MockObserver(self)

  def createHotObservable(self, *messages):
    return HotObservable(self, list(messages))

  def createColdObservable(self, *messages):
    return ColdObservable(self, list(messages))

  def start(self, factory, created=TIME_CREATE, subscribed=TIME_SUBSCRIBE, disposed=TIME_DISPOSE):
    state = Struct(
      source=None,
      subscription=None,
      observer=self.createObserver()
    )

    def scheduledCreate():
      state.source = factory()
      return Disposable.empty()

    def scheduledSubscribe():
      state.subscription = state.source.subscribe(state.observer)
      return Disposable.empty()

    def scheduledDispose():
      state.subscription.dispose()
      return Disposable.empty()

    self.scheduleWithAbsolute(created, scheduledCreate)
    self.scheduleWithAbsolute(subscribed, scheduledSubscribe)
    self.scheduleWithAbsolute(disposed, scheduledDispose)

    super(TestScheduler, self).start()

    return state.observer

  class MockObserver(Observer):
    def __init__(self, scheduler):
      super(TestScheduler.MockObserver, self).__init__()
      self.scheduler = scheduler
      self.messages = []

    def onNext(self, value):
      self.messages.append((
        self.scheduler.now(),
        OnNext(value)
      ))

    def onError(self, exception):
      self.messages.append((
        self.scheduler.now(),
        OnError(exception)
      ))

    def onCompleted(self):
      self.messages.append((
        self.scheduler.now(),
        OnCompleted()
      ))


class HotObservable(Observable):
  def __init__(self, scheduler, messages):
    super(HotObservable, self).__init__()
    self.scheduler = scheduler
    self.messages = list(messages)
    self.observers = []
    self.subscriptions = []

    def scheduled(_, message):
      # time = message[0]
      notification = message[1]

      for o in list(self.observers):
        notification.accept(o)

      return Disposable.empty()

    for m in messages:
      scheduler.scheduleWithAbsoluteAndState(m, m[0], scheduled)

  def subscribeCore(self, observer):
    index = len(self.subscriptions)

    self.observers.append(observer)
    self.subscriptions.append(Struct(
      subscribe=self.scheduler.now(),
      unsubscribe=0
    ))

    def dispose():
      self.observers.remove(observer)
      self.subscriptions[index].unsubscribe = self.scheduler.now()

    return Disposable.create(dispose)


class ColdObservable(Observable):
  def __init__(self, scheduler, messages):
    super(ColdObservable, self).__init__()
    self.scheduler = scheduler
    self.messages = messages
    self.subscriptions = []
    self.observers = []

  def subscribeCore(self, observer):
    index = len(self.subscriptions)

    self.observers.append(observer)
    self.subscriptions.append(Struct(
      subscribe=self.scheduler.now(),
      unsubscribe=0
    ))

    def scheduled(_, message):
      # time = message[0]
      notification = message[1]

      notification.accept(observer)

      return Disposable.empty()

    for m in self.messages:
      self.scheduler.scheduleWithRelativeAndState(m, m[0], scheduled)


    def dispose():
      self.observers.remove(observer)
      self.subscriptions[index].unsubscribe = self.scheduler.now()

    return Disposable.create(dispose)


class ReactiveTest(unittest.TestCase):
  def simpleHot(self, *values):
    scheduler = TestScheduler()

    def gen(start):
      while True:
        yield start
        start += 10

    messages = list(
      zip(
        gen(TestScheduler.TIME_SUBSCRIBE + 10),
        [OnNext(x) for x in values] + [OnCompleted()]
      )
    )
    observable = scheduler.createHotObservable(*messages)

    return (
      scheduler,
      observable,
      messages
    )

  def simpleCold(self, *values):
    scheduler = TestScheduler()

    def gen(start):
      while True:
        yield start
        start += 10

    messages = list(
      zip(
        gen(10),
        [OnNext(x) for x in values] + [OnCompleted()]
      )
    )
    observable = scheduler.createColdObservable(*messages)

    return (
      scheduler,
      observable,
      messages
    )

  def assertHasValues(self, observer, vals, endAt, text):
    errors = [x for x in observer.messages if x[1].kind == Notification.KIND_ERROR]

    if len(errors) > 0:
      raise errors[0][1].exception

    messages = [
      (x[0], OnNext(x[1])) for x in vals
    ]

    if endAt != None:
      messages += [
        (endAt, OnCompleted())
      ]

    self.assertSequenceEqual(messages, observer.messages, text)

  def assertHasSingleValue(self, observer, value, at, text):
    errors = [x for x in observer.messages if x[1].kind == Notification.KIND_ERROR]
    values = [x for x in observer.messages if x[1].kind == Notification.KIND_NEXT]

    if len(errors) > 0:
      raise errors[0][1].exception

    self.assertEqual(1, len(values), text)
    self.assertEqual(at, values[0][0], text)
    self.assertEqual(value, values[0][1].value, text)

  def assertHasError(self, observer, exceptionText, at, text):
    errors = [x for x in observer.messages if x[1].kind == Notification.KIND_ERROR]

    self.assertEqual(1, len(errors), text)
    self.assertEqual(at, errors[0][0], text)
    self.assertEqual(exceptionText, str(errors[0][1].exception), text)

  def assertHasRecorded(self, observer, messages, text):
    errors = [x for x in observer.messages if x[1].kind == Notification.KIND_ERROR]
    errorsExpected = [x for x in messages if x[1].kind == Notification.KIND_ERROR]

    if len(errors) > 0:
      if len(errorsExpected) == 0:
        raise errors[0][1].exception
      else:
        self.assertEqual(errorsExpected[0][0], errors[0][0], text)
        self.assertEqual(str(errorsExpected[0][1].exception), str(errors[0][1].exception), text)

    self.assertSequenceEqual(messages, observer.messages, text)
