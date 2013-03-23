import unittest
    # sys.stdout.write(str(dir(a)))
# from rx.linq import Observable
from rx.disposable import Disposable
from rx.internal import Struct
from rx.notification import Notification
from rx.observable import Observable
from rx.observer import Observer
from rx.scheduler import Scheduler
from rx.subject import Subject

def rep(value, count):
  return Observable.fromIterable([value]*count)

def OnNext(value):
  return Notification.createOnNext(value)

def OnError(exception):
  return Notification.createOnError(exception)

def OnComplete():
  return Notification.createOnCompleted()

class Recorder(Observer):
  def __init__(self, source):
    super(Recorder, self).__init__()
    self.source = source
    self.isStopped = False
    self.messages = []

  def onNext(self, value):
    assert not self.isStopped
    self.messages.append(value)

  def onError(self, exception):
    raise exception

  def onCompleted(self):
    self.isStopped = True

  def materialize(self):
    assert self.isStopped
    return self.messages

  def subscribe(self):
    return self.source.materialize().subscribe(self)


class ReactiveTest(unittest.TestCase):
  def assertHasMessages(self, observable, *messages):
    expected = list(messages)
    actual = list(observable.materialize())

    errorExpected = [x for x in expected if x.NotificationKind == Notification.KIND_ERROR]
    errorActual = [x for x in actual if x.NotificationKind == Notification.KIND_ERROR]

    if len(errorExpected) == 0 and len(errorActual) > 0:
      raise errorActual[0].exception

    self.assertSequenceEqual(expected, actual, "The observable should generate the correct messages", list)

class TestAggregation(ReactiveTest):
  def test_aggregate(self):
    o = rep(5, 4)
    s = o.aggregate(0, lambda acc, el: acc + el).wait()

    self.assertEqual(20, s, "Accumulate should yield sum")

  def test_all_true(self):
    o = rep(5, 4)
    a = o.all(lambda x: x == 5).wait()

    self.assertTrue(a, "all values should be equal to 5")

  def test_any_empty(self):
    o = Observable.empty()
    a = o.any().wait()

    self.assertFalse(a, "all values should not be equal to 4")

  def test_any_value(self):
    o = rep(5, 4)
    a = o.any().wait()

    self.assertTrue(a, "all values should be equal to 5")

  def test_any_predicate(self):
    o = rep(5, 4)
    a = o.any(lambda x: x == 3).wait()

    self.assertFalse(a, "all values should not be equal to 3")

  def test_average(self):
    o = rep(5, 4)
    a = o.average().wait()

    self.assertEqual(5, a, "average sould be 5")

  def test_contains_true(self):
    o = rep(5, 4)
    a = o.contains(5).wait()

    self.assertTrue(a, "should contain 5")

  def test_contains_false(self):
    o = rep(5, 4)
    a = o.contains(3).wait()

    self.assertFalse(a, "should not contain 3")

  def test_count(self):
    o = rep(5, 4)
    a = o.count(lambda x: x == 5).wait()

    self.assertEqual(4, a, "sequence should contain 4 elements")

  def test_first_async(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.firstAsync(lambda x: x == 2).wait()

    self.assertEqual(2, a, "first 2 in sequence should be 2")

  def test_first_async_or_default(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.firstAsyncOrDefault(lambda x: x == 5, 7).wait()

    self.assertEqual(7, a, "first 5 sould not be found, 7 sould be returned")

  def test_last_async(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.lastAsync().wait()

    self.assertEqual(1, a, "last value in sequence should be 1")

  def test_last_async_or_default(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.lastAsyncOrDefault(lambda x: x == 5, 7).wait()

    self.assertEqual(7, a, "last 5 sould not be found, 7 sould be returned")

  def test_max(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.max().wait()

    self.assertEqual(3, a, "max value should be 3")

  def test_max_by(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.maxBy(lambda x: -x).wait()

    self.assertSequenceEqual([1], a, "max inverse value should be 1")

  def test_min(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.min().wait()

    self.assertEqual(1, a, "min value should be 1")

  def test_min_by(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.minBy(lambda x: -x).wait()

    self.assertSequenceEqual([3], a, "min inverse value should be 3")

  def test_sequence_equal(self):
    o1 = rep(5, 4)
    o2 = rep(5, 4)
    a = o1.sequenceEqual(o2).wait()

    self.assertTrue(a, "sequences should be equal")

  def test_single_async(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.singleAsync(lambda x: x == 2).wait()

    self.assertEqual(2, a, "single 2 in sequence should be 2")

  def test_single_async_or_default(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.singleAsyncOrDefault(lambda x: x == 5, 7).wait()

    self.assertEqual(7, a, "single 5 sould not be found, 7 sould be returned")

  def test_sum(self):
    o = rep(5, 4)
    a = o.sum().wait()

    self.assertEqual(20, a, "sum should be 20")

  def test_to_list(self):
    o = rep(5, 4)
    a = o.toList().wait()

    self.assertSequenceEqual([5, 5, 5, 5], a, "to list should be [5, 5, 5, 5]", list)

  def test_to_dictionary(self):
    o = Observable.fromIterable([
      ('a', 1),
      ('b', 1)
    ])
    a = o.toDictionary(lambda x: x[0], lambda x: x[1]).wait()

    self.assertEqual({'a': 1, 'b': 1}, a, "dictionary should contain last values for each key")

  def test_to_dictionary_duplicate(self):
    o = Observable.fromIterable([
      ('a', 1),
      ('a', 2),
      ('b', 1)
    ])
    a = o.toDictionary(lambda x: x[0], lambda x: x[1]).wait

    self.assertRaisesRegex(Exception, "Duplicate key", a)


class TestBinding(ReactiveTest):
  def test_multicast(self):
    state = {
      'isSet1': False,
      'isSet2': False
    }

    def onNext1(_):
      state['isSet1'] = True
    def onNext2(_):
      state['isSet2'] = True

    s = Subject()
    s.subscribe(onNext1)

    o = rep(5, 4).multicast(s)
    o.subscribe(onNext2)

    self.assertFalse(state['isSet1'], "Subject should not be called before connecting")
    self.assertFalse(state['isSet2'], "OnNext should not be called before connecting")

    o.connect()
    self.assertTrue(state['isSet1'], "Subject should be called on connecting")
    self.assertTrue(state['isSet2'], "OnNext should be called on connecting")

  def test_multicast_individual(self):
    state = {
      'isSet1': False,
      'isSet2': False,
      'value1': None,
      'value2': None
    }

    def onNext1(value):
      state['isSet1'] = True
      state['value1'] = value
    def onNext2(value):
      state['isSet2'] = True
      state['value2'] = value

    s = Subject()
    s.subscribe(onNext1)

    o = rep(5, 4).multicastIndividual(lambda: s, lambda xs: xs.count())

    self.assertFalse(state['isSet1'], "Subject should not be called before connecting")
    self.assertFalse(state['isSet2'], "OnNext should not be called before connecting")

    o.subscribe(onNext2)
    o.wait()

    self.assertTrue(state['isSet1'], "Subject should be called on connecting")
    self.assertTrue(state['isSet2'], "OnNext should be called on connecting")

    self.assertEqual(5, state['value1'], "value should be count")
    self.assertEqual(4, state['value2'], "value should be 5")


  def test_publish(self):
    state = {
      'isSet1': False,
      'value1': None,
    }

    def onNext1(value):
      state['isSet1'] = True
      state['value1'] = value

    o = Observable.empty().publish(5)

    self.assertFalse(state['isSet1'], "Subject should not be called before connecting")

    o.subscribe(onNext1)
    o.connect()
    o.lastOrDefault()

    self.assertTrue(state['isSet1'], "Subject should be called on connecting")
    self.assertEqual(5, state['value1'], "value should be count")

  def test_publish_selector(self):
    state = {
      'isSet1': False,
      'value1': None,
    }

    def onNext1(value):
      state['isSet1'] = True
      state['value1'] = value

    o = rep(5, 4).publishIndividual(lambda xs: xs.count())

    self.assertFalse(state['isSet1'], "Subject should not be called before connecting")

    o.subscribe(onNext1)
    o.wait()

    self.assertTrue(state['isSet1'], "Subject should be called on connecting")
    self.assertEqual(4, state['value1'], "value should be count")

  def test_publish_last(self):
    o = Observable.fromIterable([1, 2, 3]).publishLast()

    o.connect()

    a1 = o.first()
    a2 = o.last()

    self.assertEqual(3, a1, "first should be 3")
    self.assertEqual(3, a2, "last should be 3")

  def test_ref_count(self):
    state = Struct(count=0)

    def dispose():
      state.count -= 1

    def subscribe(observer):
      state.count += 1
      return Disposable.create(dispose)

    o = Observable.create(subscribe).publish().refCount()

    self.assertEqual(0, state.count, "there should be no subscription")

    with o.subscribe(lambda x: None):
      with o.subscribe(lambda x: None):
        self.assertEqual(1, state.count, "there should be one subscription")

    self.assertEqual(0, state.count, "there should be no subscription")

  def test_replay(self):
    s = Subject()

    o = s.replay()
    o.connect()

    s.onNext(1)
    s.onNext(2)
    s.onNext(3)
    s.onCompleted()

    a1 = o.first()
    a2 = o.last()

    self.assertEqual(1, a1, "first should be 1")
    self.assertEqual(3, a2, "last should be 3")


class TestBlocking(ReactiveTest):
  def test_collect(self):
    def getInitialCollector():
      return []
    def merge(acc, val):
      return acc + [val]
    def getNewCollector(acc):
      return []

    o = rep(5, 4)
    a = []

    for acc in o.collect(getInitialCollector, merge, getNewCollector):
       a += acc

    self.assertSequenceEqual([5, 5, 5, 5], a, "collected array should be [5]*4", list)

  def test_first(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.first(lambda x: x == 2)

    self.assertEqual(2, a, "first 2 in sequence should be 2")

  def test_first_or_default(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.firstOrDefault(lambda x: x == 5, 7)

    self.assertEqual(7, a, "first 5 sould not be found, 7 sould be returned")

  def test_for_each(self):
    acc = []
    values = [3, 2, 1]

    def it(value):
      acc.append(value)

    o = Observable.fromIterable(values)
    o.forEach(it)

    self.assertSequenceEqual(values, acc, "accumulator should equal values", list)

  def test_for_each_enumerate(self):
    values = [3, 2, 1]
    state = Struct(
      acc=[],
      index=0
    )

    def it(value, index):
      state.acc.append(value)
      state.index = index

    o = Observable.fromIterable(values)
    o.forEachEnumerate(it)

    self.assertSequenceEqual(values, state.acc, "accumulator should equal values", list)
    self.assertEqual(2, state.index, "last index set should be 2")

  def test_get_iterator(self):
    values = [3, 2, 1]
    o = Observable.fromIterable(values)
    a = list(o.getIterator())

    self.assertSequenceEqual(values, a, "getIterator should return values", list)

  def test_last(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.last()

    self.assertEqual(1, a, "last value in sequence should be 1")

  def test_last_or_default(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.lastOrDefault(lambda x: x == 5, 7)

    self.assertEqual(7, a, "last 5 sould not be found, 7 sould be returned")

  def test_single(self):
    o = Observable.fromIterable([3, 2, 1])
    self.assertRaises(Exception, o.single, None, None)

  def test_single_or_default(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.singleOrDefault(lambda x: x == 5, 7)

    self.assertEqual(7, a, "single 5 sould not be found, 7 sould be returned")


class TestConcurrency(ReactiveTest):
  def test_subscribe_on(self):
    state = Struct(wasScheduled=False)

    class Sched(Scheduler):
      def schedule(self, action):
        state.wasScheduled = True

    o = Observable.fromIterable([3, 2, 1]).subscribeOn(Sched())

    with o.subscribe(lambda x: None):
      pass

    self.assertTrue(state.wasScheduled, "subscribeOn should schedule subscription on provided scheduler")

  def test_observe_on(self):
    state = Struct(loopScheduled=False)

    class Sched(Scheduler):
      isLongRunning = True

      def scheduleLongRunning(self, action):
        state.loopScheduled = True

    o = Observable.fromIterable([3, 2, 1]).observeOn(Sched())

    with o.subscribe(lambda x: None):
      pass

    self.assertTrue(state.loopScheduled, "observeOn should schedule onNext on provided scheduler")

  def test_synchronize(self):
    state = Struct(wasLocked=False)

    class DummyLock(object):
      def __enter__(self):
        state.wasLocked = True

      def __exit__(self, exc, a, b):
        pass

    o = Observable.fromIterable([3, 2, 1]).synchronize(DummyLock())

    with o.subscribe(lambda x: None):
      pass

    self.assertTrue(state.wasLocked, "synchronize should use the lock provided")


class TestCreation(ReactiveTest):
    # Only use setUp() and tearDown() if necessary

    # def setUp(self):
    #     ... code to execute in preparation for tests ...

    # def tearDown(self):
    #     ... code to execute to clean up after tests ...

  def test_create(self):
    state = Struct(
      subscribeCalled=False,
      disposeCalled=False
    )

    def subscribe(observer):
      state.subscribeCalled = True

      def dispose():
        state.disposeCalled = True

      return dispose

    o = Observable.create(subscribe)

    with o.subscribe(lambda x: None):
      self.assertTrue(state.subscribeCalled, "create should call provided subscribe method")

    self.assertTrue(state.disposeCalled, "create should call the provided dispose method")

  def test_defer(self):
    values = [3, 2, 1]
    state = Struct(deferCalled=False)

    def defered():
      state.deferCalled = True
      return Observable.fromIterable(values)

    o = Observable.defer(defered)
    a = o.toList().wait()

    self.assertSequenceEqual(values, a, "defere should return the created observable sequence", list)

  def test_empty(self):
    self.assertHasMessages(
      Observable.empty(),
      OnComplete()
    )

  def test_generate(self):
    def condition(x):
      return x < 3
    def iterate(x):
      return x + 1
    def resultSelector(x):
      return x

    o = Observable.generate(0, condition, iterate, resultSelector)

    self.assertHasMessages(
      o,
      OnNext(0),
      OnNext(1),
      OnNext(2),
      OnComplete()
    )

  def test_range(self):
    self.assertHasMessages(
      Observable.range(1, 3),
      OnNext(0),
      OnNext(1),
      OnNext(2),
      OnComplete()
    )

  def test_repeat(self):
    self.assertHasMessages(
      Observable.repeat(5, 4),
      OnNext(5),
      OnNext(5),
      OnNext(5),
      OnNext(5),
      OnComplete()
    )

  def test_return(self):
    self.assertHasMessages(
      Observable.returnValue(5),
      OnNext(5),
      OnComplete()
    )

  def test_throw(self):
    ex = Exception("")

    self.assertHasMessages(
      Observable.throw(ex),
      OnError(ex)
    )

  def test_using(self):
    def dispose():
      state.resourceDisposed = True

    state = Struct(
      resourceCreated=False,
      resourceDisposed=False,
      resourceWasState=False,
      dispose=dispose
    )

    def createResource():
      state.resourceCreated = True
      return state

    def createObservable(resource):
      state.resourceWasState = resource is state

      def subscribe(observer):
        return Disposable.empty()

      return Observable.create(subscribe)

    with Observable.using(createResource, createObservable).subscribe():
      self.assertTrue(state.resourceCreated, "using should use resource factory")
      self.assertTrue(state.resourceWasState, "using should foreward created resource to observable factory")

    self.assertTrue(state.resourceDisposed, "using should dispose resource")

  def test_from_iterable(self):
    values = [1, 2, 3]

    self.assertHasMessages(
      Observable.fromIterable(values),
      OnNext(1),
      OnNext(2),
      OnNext(3),
      OnComplete()
    )

    # We do it twice to test if we can reiterate the iterable
    self.assertHasMessages(
      Observable.fromIterable(values),
      OnNext(1),
      OnNext(2),
      OnNext(3),
      OnComplete()
    )

  def test_from_event(self):
    state = Struct(
      handler=None,
      receivedValue=None
    )

    def addHandler(h):
      self.assertIsNone(state.handler, "fromEvent should only attach the handler once")
      state.handler = h

    def removeHandler(h):
      self.assertIs(state.handler, h, "fromEvent should remove the correct handler")
      state.handler = None

    def onNext(value):
      state.receivedValue = value

    o = Observable.fromEvent(addHandler, removeHandler)

    with o.subscribe(onNext, self.fail):
      self.assertIsNotNone(state.handler, "fromEvent should attach a handler")
      state.handler(5)

    self.assertEqual(5, state.receivedValue, "fromEvent should foreward event value")
    self.assertIsNone(state.handler, "fromEvent should remove the handler")


class TestImperative(ReactiveTest):
  def test_case(self):
    selector = lambda: 5
    sources = {
      5: Observable.fromIterable([3, 2, 1]),
      4: Observable.fromIterable([6, 5, 4])
    }

    self.assertHasMessages(
      Observable.case(selector, sources),
      OnNext(3),
      OnNext(2),
      OnNext(1),
      OnComplete()
    )

  def test_doWhile(self):
    state = Struct(count=4)

    def condition():
      state.count -= 1
      return state.count >= 0

    self.assertHasMessages(
      Observable.returnValue(5).doWhile(condition),
      OnNext(5),
      OnNext(5),
      OnNext(5),
      OnNext(5),
      OnNext(5),
      OnComplete()
    )

  def test_iterable_for(self):
    self.assertHasMessages(
      Observable.iterableFor(range(1, 5), lambda x: Observable.returnValue(x)),
      OnNext(1),
      OnNext(2),
      OnNext(3),
      OnNext(4),
      OnComplete()
    )

  def test_branch(self):
    def condition():
      return False

    thenSource = Observable.returnValue(5)
    elseSource = Observable.returnValue(6)

    self.assertHasMessages(
      Observable.branch(condition, thenSource, elseSource),
      OnNext(6),
      OnComplete()
    )

  def test_loop(self):
    state = Struct(count=4)

    def condition():
      state.count -= 1
      return state.count >= 0

    self.assertHasMessages(
      Observable.returnValue(5).loop(condition),
      OnNext(5),
      OnNext(5),
      OnNext(5),
      OnNext(5),
      OnComplete()
    )


class TestMultiple(ReactiveTest):
  def test_amb(self):
    s1 = Subject()
    s2 = Subject()

    r = Recorder(s1.amb(s2))

    with r.subscribe():
      s1.onNext(4)
      s2.onNext(5)
      s1.onNext(6)
      s1.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(4),
      OnNext(6),
      OnComplete()
    )

  def test_catch_exception(self):
    state = Struct(
      exception=None
    )
    ex = Exception("Test Exception")

    def handler(exception):
      state.exception = exception
      return Observable.throw(ex).startWith(5)

    s = Subject()
    r = Recorder(s.catchException(handler))

    with r.subscribe():
      s.onNext(4)
      s.onError(ex)

    self.assertIs(ex, state.exception)
    self.assertHasMessages(
      r,
      OnNext(4),
      OnNext(5),
      OnError(ex)
    )

  def test_catch_fallback(self):
    ex = Exception("Test Exception")
    observables = [
      Observable.throw(ex),
      Observable.returnValue(5)
    ]

    self.assertHasMessages(
      Observable.throw(ex).catchFallback(observables),
      OnNext(5),
      OnComplete()
    )

  def test_combine_latest(self):
    s1 = Subject()
    s2 = Subject()

    o = Observable.combineLatest(s1, s2)
    r = Recorder(o)

    with r.subscribe():
      s1.onNext(5)
      s2.onNext(4)
      s2.onNext(3)
      s2.onCompleted()
      s1.onNext(6)
      s1.onCompleted()

    self.assertHasMessages(
      r,
      OnNext((5, 4)),
      OnNext((5, 3)),
      OnNext((6, 3)),
      OnComplete()
    )

  def test_concat(self):
    o1 = Observable.returnValue(4)
    o2 = Observable.returnValue(5)
    o3 = Observable.returnValue(6)

    self.assertHasMessages(
      o1.concat(o2, o3),
      OnNext(4),
      OnNext(5),
      OnNext(6),
      OnComplete()
    )

    self.assertHasMessages(
      o1.concat([o2, o3]),
      OnNext(4),
      OnNext(5),
      OnNext(6),
      OnComplete()
    )

    self.assertHasMessages(
      Observable.concat(o1, o2, o3),
      OnNext(4),
      OnNext(5),
      OnNext(6),
      OnComplete()
    )

    self.assertHasMessages(
      Observable.concat([o1, o2, o3]),
      OnNext(4),
      OnNext(5),
      OnNext(6),
      OnComplete()
    )

  def test_merge(self):
    s1 = Subject()
    s2 = Subject()

    r = Recorder(Observable.merge(Observable.fromIterable([s1, s2])))

    with r.subscribe():
      s1.onNext(3)
      s2.onNext(4)
      s1.onNext(6)
      s1.onCompleted()
      s2.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(3),
      OnNext(4),
      OnNext(6),
      OnComplete()
    )

  def test_on_error_resume_next(self):
    ex = Exception("Test Exception")
    os = [
      Observable.throw(ex),
      Observable.throw(ex),
      Observable.throw(ex),
      Observable.returnValue(4),
    ]

    r = Recorder(Observable.onErrorResumeNext(os))

    with r.subscribe():
      pass

    self.assertHasMessages(
      r,
      OnNext(4),
      OnComplete()
    )

  def test_skip_until(self):
    s1 = Subject()
    s2 = Subject()

    r = Recorder(s1.skipUntil(s2))

    with r.subscribe():
      s1.onNext(1)
      s2.onNext(3)
      s1.onNext(2)
      s1.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(2),
      OnComplete()
    )

  def test_switch(self):
    s = Subject()
    s1 = Subject()
    s2 = Subject()

    r = Recorder(s.switch())

    with r.subscribe():
      s.onNext(s1)

      s1.onNext(1)

      # should be ignored
      s2.onNext(5)

      s.onNext(s2)

      # should be ignored
      s1.onNext(2)

      s2.onNext(6)

      s2.onCompleted()
      s.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(1),
      OnNext(6),
      OnComplete()
    )

  def test_take_until(self):
    s1 = Subject()
    s2 = Subject()

    r = Recorder(s1.takeUntil(s2))

    with r.subscribe():
      s1.onNext(1)
      s2.onNext(3)
      s1.onNext(2)
      s1.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(1),
      OnComplete()
    )

  def test_zip(self):
    o1 = Observable.fromIterable([1, 2])
    o2 = Observable.fromIterable([1, 2, 3])

    r = Recorder(Observable.zip(o1, o2))

    with r.subscribe():
      pass

    self.assertHasMessages(
      r,
      OnNext((1, 1)),
      OnNext((2, 2)),
      OnComplete()
    )















    # import pdb; pdb.set_trace()
    # import sys; sys.stdout.write(observer)



if __name__ == '__main__':
    unittest.main()