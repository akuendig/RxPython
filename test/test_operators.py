import unittest
    # sys.stdout.write(str(dir(a)))
# from rx.linq import Observable
from rx.disposable import Disposable
from rx.internal import Struct
from rx.observable import Observable
from rx.scheduler import Scheduler
from rx.subject import Subject

from test.reactive import OnNext, OnError, OnCompleted, TestScheduler, ReactiveTest

def rep(value, count):
  return Observable.fromIterable([value]*count)

class TestAggregation(ReactiveTest):
  def test_aggregate(self):
    sched, xs, messages = self.simpleHot(5, 5, 5, 5)

    o = sched.start(lambda: xs.aggregate(0, lambda acc, el: acc + el))

    self.assertHasSingleValue(o, 20, messages[-1][0],
      "accumulate should yield result"
    )

  def test_all_true(self):
    sched, xs, messages = self.simpleHot(5, 5, 5, 5)

    o = sched.start(lambda: xs.all(lambda x: x == 5))

    self.assertHasSingleValue(o, True, messages[-1][0],
      "all should test all values"
    )

  def test_any_empty(self):
    sched, xs, messages = self.simpleHot()

    o = sched.start(lambda: xs.any())

    self.assertHasSingleValue(o, False, messages[-1][0],
      "any on emtpy sequence should yield False"
    )

  def test_any_value(self):
    sched = TestScheduler()

    sched, xs, messages = self.simpleHot(5, 5, 5, 5)

    o = sched.start(lambda: xs.any())

    self.assertHasSingleValue(o, True, messages[0][0],
      "any without predicate and with elements should yield True"
    )

  def test_any_predicate(self):
    sched, xs, messages = self.simpleHot(5, 5, 5, 5)

    o = sched.start(lambda: xs.any(lambda x: x == 3))

    self.assertHasSingleValue(o, False, messages[-1][0],
      "any should test predicate on all values"
    )

  def test_average(self):
    sched, xs, messages = self.simpleHot(5, 5, 5, 5)

    o = sched.start(lambda: xs.average())

    self.assertHasSingleValue(o, 5, messages[-1][0],
      "average should yield average"
    )

  def test_contains_true(self):
    sched, xs, messages = self.simpleHot(5, 5, 5, 5)

    o = sched.start(lambda: xs.contains(5))

    self.assertHasSingleValue(o, True, messages[0][0],
      "contains should find value"
    )

  def test_contains_false(self):
    sched, xs, messages = self.simpleHot(5, 5, 5, 5)

    o = sched.start(lambda: xs.contains(3))

    self.assertHasSingleValue(o, False, messages[-1][0],
      "contains should not find non existent value"
    )

  def test_count(self):
    sched, xs, messages = self.simpleHot(5, 5, 5, 5)

    o = sched.start(lambda: xs.count(lambda x: x == 5))

    self.assertHasSingleValue(o, 4, messages[-1][0],
      "count should count all values"
    )

  def test_first_async(self):
    sched, xs, messages = self.simpleHot(3, 2, 1)

    o = sched.start(lambda: xs.firstAsync(lambda x: x == 2))

    self.assertHasSingleValue(o, 2, messages[1][0],
      "first should yield first found value"
    )

  def test_first_async_or_default(self):
    sched, xs, messages = self.simpleHot(5, 5, 5, 5)

    o = sched.start(lambda: xs.firstAsyncOrDefault(lambda x: x == 3, 7))

    self.assertHasSingleValue(o, 7, messages[-1][0],
      "firstOrDefault should yield default value if not found"
    )

  def test_last_async(self):
    sched, xs, messages = self.simpleHot(3, 2, 1)

    o = sched.start(lambda: xs.lastAsync())

    self.assertHasSingleValue(o, 1, messages[3][0],
      "lastAsync should yield last value"
    )

  def test_last_async_or_default(self):
    sched, xs, messages = self.simpleHot(5, 5, 5, 5)

    o = sched.start(lambda: xs.lastAsyncOrDefault(lambda x: x == 3, 7))

    self.assertHasSingleValue(o, 7, messages[-1][0],
      "lastAsyncOrDefault should yield default value if not found"
    )

  def test_max(self):
    sched, xs, messages = self.simpleHot(3, 2, 1)

    o = sched.start(lambda: xs.max())

    self.assertHasSingleValue(o, 3, messages[-1][0],
      "max should yield maximum"
    )

  def test_max_by(self):
    sched, xs, messages = self.simpleHot(3, 2, 1)

    o = sched.start(lambda: xs.maxBy(lambda x: -x))

    self.assertHasSingleValue(o, [1], messages[-1][0],
      "maxBy should yield list of max values by key"
    )

  def test_min(self):
    sched, xs, messages = self.simpleHot(3, 2, 1)

    o = sched.start(lambda: xs.min())

    self.assertHasSingleValue(o, 1, messages[-1][0],
      "min should yield minimum"
    )

  def test_min_by(self):
    sched, xs, messages = self.simpleHot(3, 2, 1)

    o = sched.start(lambda: xs.minBy(lambda x: -x))

    self.assertHasSingleValue(o, [3], messages[-1][0],
      "minBy should yield list of min values by key"
    )

  def test_sequence_equal(self):
    sched = TestScheduler()

    xs = sched.createHotObservable(
      (210, OnNext(1)),
      (230, OnCompleted())
    )

    ys = sched.createHotObservable(
      (220, OnNext(1)),
      (240, OnCompleted())
    )

    o = sched.start(lambda: xs.sequenceEqual(ys))

    self.assertHasSingleValue(o, True, 240,
      "sequenceEqual should yield True on equal sequences"
    )

  def test_single_async(self):
    sched, xs, messages = self.simpleHot(3, 2, 1)

    o = sched.start(lambda: xs.singleAsync(lambda x: x == 2))

    self.assertHasSingleValue(o, 2, messages[-1][0],
      "single should yield single value"
    )

  def test_single_async_or_default(self):
    sched, xs, messages = self.simpleHot(3, 2, 1)

    o = sched.start(lambda: xs.singleAsyncOrDefault(lambda x: x == 5, 7))

    self.assertHasSingleValue(o, 7, messages[-1][0],
      "singleAsyncOrDefault should yield default value if not found"
    )

  def test_sum(self):
    sched, xs, messages = self.simpleHot(5, 5, 5, 5)

    o = sched.start(lambda: xs.sum())

    self.assertHasSingleValue(o, 20, messages[-1][0],
      "sum should yield sum"
    )

  def test_to_list(self):
    sched, xs, messages = self.simpleHot(1, 2, 3)

    o = sched.start(lambda: xs.toList())

    self.assertHasSingleValue(o, [1, 2, 3], messages[-1][0],
      "toList should yield list of all values"
    )

  def test_to_dictionary(self):
    sched, xs, messages = self.simpleHot(
      ('a', 1),
      ('b', 1)
    )

    o = sched.start(lambda: xs.toDictionary(lambda x: x[0], lambda x: x[1]))

    self.assertHasSingleValue(o, {'a': 1, 'b': 1}, messages[-1][0],
      "toDictionary should yield dictionary of all values"
    )

  def test_to_dictionary_duplicate(self):
    sched, xs, messages = self.simpleHot(
      ('a', 1),
      ('a', 2),
      ('b', 1)
    )

    o = sched.start(lambda: xs.toDictionary(lambda x: x[0], lambda x: x[1]))

    self.assertHasError(
      o,
      "Duplicate key 'a'",
      messages[1][0],
      "toDictionary should yield error on duplicate key"
    )


class TestBinding(ReactiveTest):
  def test_multicast(self):
    sched, xs, messages = self.simpleHot(1, 2, 3, 4, 5)

    xs = xs.multicast(Subject())
    sched.scheduleAbsolute(215, lambda: xs.connect())

    o = sched.start(lambda: xs)

    self.assertHasValues(o, [
        (220, 2),
        (230, 3),
        (240, 4),
        (250, 5),
      ],
      messages[-1][0],
      "multicast should wait for connect call"
    )

  def test_multicast_individual(self):
    sched, xs, messages = self.simpleHot(1, 2, 3, 4, 5)

    o = sched.start(
      lambda: xs.multicastIndividual(
        lambda: Subject(),
        lambda xs: xs.zip(xs).select(sum)
      )
    )

    self.assertHasValues(o, [
        (210, 2),
        (220, 4),
        (230, 6),
        (240, 8),
        (250, 10),
      ],
      messages[-1][0],
      "multicastIndividual should apply selector"
    )

  def test_publish(self):
    sched = TestScheduler()
    xs = sched.createHotObservable(
      (190, OnNext(1)),
      (210, OnNext(1)),
      (220, OnNext(1))
    )

    xs = xs.publish(5)
    sched.scheduleAbsolute(215, lambda: xs.connect())

    o = sched.start(
      lambda: xs
    )

    self.assertHasValues(o, [
        (200, 5),
        (220, 1),
      ],
      None,
      "publish should send initial value on subscribe, ignore values before connect, send values after connct"
    )

  def test_publish_individual(self):
    sched, xs, messages = self.simpleHot(1, 2, 3, 4, 5)

    o = sched.start(
      lambda: xs.publishIndividual(
        lambda xs: xs.zip(xs).select(sum)
      )
    )

    self.assertHasValues(o, [
        (210, 2),
        (220, 4),
        (230, 6),
        (240, 8),
        (250, 10),
      ],
      messages[-1][0],
      "publishIndividual should apply the selector and not need a connect"
    )

  def test_publish_last(self):
    sched, xs, messages = self.simpleHot(1, 2, 3, 4, 5)

    xs = xs.publishLast()
    sched.scheduleAbsolute(215, lambda: xs.connect())

    o = sched.start(
      lambda: xs
    )
    endAt = messages[-1][0]

    self.assertHasValues(o, [
        (endAt, 5)
      ],
      endAt,
      "publishLast should wait for connect call and the return last value"
    )

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
    sched, xs, messages = self.simpleHot(1, 2, 3, 4, 5)

    xs = xs.replay()
    sched.scheduleAbsolute(215, lambda: xs.connect())

    o = sched.start(
      lambda: xs,
      subscribed=250
    )

    self.assertHasValues(o, [
        (250, 2),
        (250, 3),
        (250, 4),
        (250, 5)
      ],
      messages[-1][0],
      "replay should replay all values since subscribe"
    )


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
    sched = TestScheduler()

    o = sched.start(
      lambda: Observable.empty()
    )

    self.assertHasRecorded(o, [
        (200, OnCompleted())
      ],
      "empty should yield no values"
    )

  def test_generate(self):
    def condition(x):
      return x < 3
    def iterate(x):
      return x + 1
    def resultSelector(x):
      return x

    sched = TestScheduler()

    o = sched.start(
      lambda: Observable.generate(0, condition, iterate, resultSelector)
    )

    self.assertHasValues(o, [
        (200, 0),
        (200, 1),
        (200, 2),
      ],
      200,
      "generate should generate values"
    )

  def test_range(self):
    sched = TestScheduler()

    o = sched.start(
      lambda: Observable.range(1, 3)
    )

    self.assertHasValues(o, [
        (200, 1),
        (200, 2),
        (200, 3),
      ],
      200,
      "range should range over values"
    )

  def test_repeat_value(self):
    sched = TestScheduler()

    o = sched.start(
      lambda: Observable.repeatValue(5, 4)
    )

    self.assertHasValues(o, [
        (200, 5),
        (200, 5),
        (200, 5),
        (200, 5),
      ],
      200,
      "repeat should repeat value"
    )

  def test_return_value(self):
    sched = TestScheduler()

    o = sched.start(
      lambda: Observable.returnValue(5)
    )

    self.assertHasValues(o, [
        (200, 5),
      ],
      200,
      "return should return value"
    )

  def test_throw(self):
    ex = Exception("Test Exception")
    sched = TestScheduler()

    o = sched.start(
      lambda: Observable.throw(ex)
    )

    self.assertHasError(
      o,
      "Test Exception",
      200,
      "throw should yield error"
    )

  def test_using(self):
    sched = TestScheduler()

    def dispose():
      state.resourceDisposed = True

    state = Struct(
      resourceCreated=False,
      resourceDisposed=False,
      dispose=dispose
    )

    def createResource():
      state.resourceCreated = True
      return state

    def createObservable(resource):
      def subscribe(observer):
        observer.onNext(resource)
        observer.onCompleted()
        return Disposable.empty()

      self.assertEqual(state, resource, "using should foreward created resource to observable factory")
      return Observable.create(subscribe)

    o = sched.start(
      lambda: Observable.using(createResource, createObservable)
    )

    self.assertTrue(state.resourceCreated, "using should use resource factory")
    self.assertTrue(state.resourceDisposed, "using should dispose resource")

    self.assertHasSingleValue(
      o,
      state,
      200,
      "using should subscribe to the created observable"
    )

  def test_from_iterable(self):
    sched = TestScheduler()
    values = [1, 2, 3]

    o = sched.start(
      lambda: Observable.fromIterable(values)
    )

    self.assertHasValues(o, [
        (200, 1),
        (200, 2),
        (200, 3),
      ],
      200,
      "fromIterable should yield all values"
    )

  def test_from_event(self):
    sched = TestScheduler()
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

    sched.scheduleAbsolute(210, lambda: state.handler(4))

    o = sched.start(
      lambda: Observable.fromEvent(addHandler, removeHandler)
    )

    self.assertHasValues(o, [
        (210, 4),
      ],
      None,
      "fromEvent should yield all values"
    )


class TestImperative(ReactiveTest):
  def test_case(self):
    sched = TestScheduler()
    selector = lambda: 5
    sources = {
      5: Observable.fromIterable([3, 2, 1]),
      4: Observable.fromIterable([6, 5, 4])
    }

    o = sched.start(
      lambda: Observable.case(selector, sources)
    )

    self.assertHasValues(o, [
        (200, 3),
        (200, 2),
        (200, 1),
      ],
      200,
      "case should yield all values from the correct observable"
    )

  def test_doWhile(self):
    sched = TestScheduler()
    state = Struct(count=4)

    def condition():
      state.count -= 1
      return state.count >= 0

    o = sched.start(
      lambda: Observable.returnValue(5).doWhile(condition)
    )

    self.assertHasValues(o, [
        (200, 5),
        (200, 5),
        (200, 5),
        (200, 5),
        (200, 5),
      ],
      200,
      "doWhile should yield self as long as condition returns True"
    )

  def test_iterable_for(self):
    sched = TestScheduler()

    o = sched.start(
      lambda: Observable.iterableFor(range(1, 5), lambda x: Observable.returnValue(x))
    )

    self.assertHasValues(o, [
        (200, 1),
        (200, 2),
        (200, 3),
        (200, 4),
      ],
      200,
      "iterableFor should yield observable from selector for each value in iterable"
    )

  def test_branch(self):
    sched = TestScheduler()
    def condition():
      return False

    thenSource = Observable.returnValue(5)
    elseSource = Observable.returnValue(6)

    o = sched.start(
      lambda: Observable.branch(condition, thenSource, elseSource)
    )

    self.assertHasValues(o, [
        (200, 6),
      ],
      200,
      "branch should subscribe to right branch on False"
    )

  def test_loop(self):
    sched = TestScheduler()
    state = Struct(count=4)

    def condition():
      state.count -= 1
      return state.count >= 0

    o = sched.start(
      lambda: Observable.returnValue(5).doWhile(condition)
    )

    self.assertHasValues(o, [
        (200, 5),
        (200, 5),
        (200, 5),
        (200, 5),
        (200, 5),
      ],
      200,
      "loop should yield self as long as condition returns True"
    )


class TestMultiple(ReactiveTest):
  def test_amb(self):
    sched = TestScheduler()
    o1 = sched.createHotObservable(
      (210, OnNext(1)),
      (250, OnNext(2)),
      (260, OnCompleted())
    )
    o2 = sched.createHotObservable(
      (240, OnNext(10)),
      (240, OnNext(20)),
      (250, OnCompleted())
    )

    o = sched.start(
      lambda: o1.amb(o2)
    )

    self.assertHasValues(o, [
        (210, 1),
        (250, 2),
      ],
      260,
      "amb should subscribe to the earliest reacting observable"
    )

  def test_catch_exception(self):
    sched = TestScheduler()
    ex = Exception("Test Exception")

    def handler(exception):
      self.assertEqual(ex, exception, "catchException should yield exception to handler")
      return Observable.throw(ex).startWith(5)

    o = sched.start(
      lambda: Observable.throw(ex).catchException(handler)
    )

    self.assertSequenceEqual(
      o.messages,
      [
        (200, OnNext(5)),
        (200, OnError(ex)),
      ],
      "catchException should only catch exceptions from the original source"
    )

  def test_catch_fallback(self):
    sched = TestScheduler()
    ex = Exception("Test Exception")
    observables = [
      Observable.throw(ex),
      Observable.returnValue(5)
    ]

    o = sched.start(
      lambda: Observable.throw(ex).catchFallback(observables)
    )

    self.assertHasValues(o, [
        (200, 5)
      ],
      200,
      "catchFallback should fall back until a succeeding sequence is found"
    )

  def test_combine_latest(self):
    sched = TestScheduler()
    o1 = sched.createHotObservable(
      (210, OnNext(1)),
      (240, OnNext(2)),
      (250, OnCompleted())
    )
    o2 = sched.createHotObservable(
      (220, OnNext(10)),
      (230, OnNext(20)),
      (240, OnCompleted())
    )

    o = sched.start(
      lambda: Observable.combineLatest(o1, o2)
    )

    self.assertHasValues(o, [
        (220, (1, 10)),
        (230, (1, 20)),
        (240, (2, 20)),
      ],
      250,
      "combineLatest should yield tuple of most latest values of all sequences"
    )

  def test_concat_1(self):
    sched = TestScheduler()
    o1 = sched.createHotObservable(
      (210, OnNext(4)),
      (240, OnCompleted())
    )
    o2 = sched.createHotObservable(
      (230, OnNext(5)),
      (250, OnCompleted())
    )
    o3 = sched.createHotObservable(
      (260, OnNext(6)),
      (270, OnCompleted())
    )

    o = sched.start(
      lambda: o1.concat(o2, o3)
    )

    self.assertHasValues(o, [
        (210, 4),
        (260, 6),
      ],
      270,
      "concat should yield values in order, ignore too early values"
    )

  def test_concat_2(self):
    sched = TestScheduler()
    o1 = sched.createHotObservable(
      (210, OnNext(4)),
      (240, OnCompleted())
    )
    o2 = sched.createHotObservable(
      (230, OnNext(5)),
      (250, OnCompleted())
    )
    o3 = sched.createHotObservable(
      (260, OnNext(6)),
      (270, OnCompleted())
    )

    o = sched.start(
      lambda: Observable.concat(o1, o2, o3)
    )

    self.assertHasValues(o, [
        (210, 4),
        (260, 6),
      ],
      270,
      "concat should yield values in order, ignore too early values"
    )

  def test_concat_3(self):
    sched = TestScheduler()
    o1 = sched.createHotObservable(
      (210, OnNext(4)),
      (240, OnCompleted())
    )
    o2 = sched.createHotObservable(
      (230, OnNext(5)),
      (250, OnCompleted())
    )
    o3 = sched.createHotObservable(
      (260, OnNext(6)),
      (270, OnCompleted())
    )

    o = sched.start(
      lambda: o1.concat([o2, o3])
    )

    self.assertHasValues(o, [
        (210, 4),
        (260, 6),
      ],
      270,
      "concat should yield values in order, ignore too early values"
    )

  def test_concat_4(self):
    sched = TestScheduler()
    o1 = sched.createHotObservable(
      (210, OnNext(4)),
      (240, OnCompleted())
    )
    o2 = sched.createHotObservable(
      (230, OnNext(5)),
      (250, OnCompleted())
    )
    o3 = sched.createHotObservable(
      (260, OnNext(6)),
      (270, OnCompleted())
    )

    o = sched.start(
      lambda: Observable.concat([o1, o2, o3])
    )

    self.assertHasValues(o, [
        (210, 4),
        (260, 6),
      ],
      270,
      "concat should yield values in order, ignore too early values"
    )

  def test_merge(self):
    sched = TestScheduler()
    o1 = sched.createHotObservable(
      (230, OnNext(4)),
      (270, OnCompleted())
    )
    o2 = sched.createHotObservable(
      (250, OnNext(5)),
      (260, OnCompleted())
    )
    o3 = sched.createHotObservable(
      (240, OnNext(6)),
      (250, OnCompleted())
    )
    o4 = sched.createHotObservable(
      (205, OnNext(o1)),
      (215, OnNext(o2)),
      (225, OnNext(o3)),
      (240, OnCompleted())
    )

    o = sched.start(
      lambda: o4.merge()
    )

    self.assertHasValues(o, [
        (230, 4),
        (240, 6),
        (250, 5),
      ],
      270,
      "merge should yield all values in order"
    )

  def test_on_error_resume_next(self):
    sched = TestScheduler()
    ex = Exception("Test Exception")
    os = [
      sched.createHotObservable((210, OnError(ex))),
      sched.createHotObservable((220, OnError(ex))),
      sched.createHotObservable((230, OnNext(2)), (240, OnCompleted())),
    ]

    o = sched.start(
      lambda: Observable.onErrorResumeNext(os)
    )

    self.assertHasValues(o, [
        (230, 2),
      ],
      240,
      "onErrorResumeNext should yield all values in order"
    )

  def test_skip_until(self):
    sched = TestScheduler()
    o1 = sched.createHotObservable(
      (210, OnNext(1)),
      (230, OnNext(2)),
      (240, OnNext(3)),
      (240, OnCompleted())
    )
    o2 = sched.createHotObservable(
      (220, OnNext(6))
    )

    o = sched.start(
      lambda: o1.skipUntil(o2)
    )

    self.assertHasValues(o, [
        (230, 2),
        (240, 3),
      ],
      240,
      "skipUntil should yield values after other observable yielded first value"
    )

  def test_switch(self):
    sched = TestScheduler()
    o1 = sched.createHotObservable(
      (230, OnNext(1)),
      (230, OnCompleted())
    )
    o2 = sched.createHotObservable(
      (240, OnNext(2)),
      (240, OnCompleted())
    )
    o3 = sched.createHotObservable(
      (210, OnNext(o1)),
      (220, OnNext(o2)),
      (220, OnCompleted())
    )

    o = sched.start(
      lambda: o3.switch()
    )

    self.assertHasValues(o, [
        (240, 2),
      ],
      240,
      "switch should always subscribe to the latest observable"
    )

  def test_take_until(self):
    sched = TestScheduler()
    o1 = sched.createHotObservable(
      (210, OnNext(1)),
      (230, OnNext(2)),
      (240, OnNext(3)),
      (240, OnCompleted())
    )
    o2 = sched.createHotObservable(
      (220, OnNext(6))
    )

    o = sched.start(
      lambda: o1.takeUntil(o2)
    )

    self.assertHasValues(o, [
        (210, 1),
      ],
      220,
      "takeUntil should yield values until other observable yielded first value"
    )

  def test_zip(self):
    sched = TestScheduler()
    o1 = sched.createHotObservable(
      (210, OnNext(1)),
      (230, OnNext(2)),
      (240, OnNext(3)),
      (250, OnCompleted())
    )
    o2 = sched.createHotObservable(
      (220, OnNext(6)),
      (230, OnNext(7)),
      (240, OnCompleted())
    )

    o = sched.start(
      lambda: o1.zip(o2)
    )

    self.assertHasValues(o, [
        (220, (1, 6)),
        (230, (2, 7)),
      ],
      250,
      "zip should yield tuples of next values of all observables"
    )


class TestSingle(ReactiveTest):
  def test_as_observable(self):
    sched, xs, messages = self.simpleHot(1, 2, 3)

    o = sched.start(
      lambda: xs.asObservable()
    )

    self.assertHasRecorded(o, messages, "asObservable should behave as original observable")

  def test_buffer(self):
    sched, xs, messages = self.simpleHot(1, 2, 3)

    o = sched.start(
      lambda: xs.buffer(2)
    )

    self.assertHasValues(o, [
        (220, [1, 2]),
        (240, [3]),
      ],
      240,
      "buffer should buffer values with count"
    )

  def test_dematerialize(self):
    ex = Exception("Test Exception")
    sched = TestScheduler()
    o1 = sched.createHotObservable(
      (210, OnNext(OnNext(1))),
      (250, OnNext(OnError(ex)))
    )

    o = sched.start(
      lambda: o1.dematerialize()
    )

    self.assertHasRecorded(o, [
        (210, OnNext(1)),
        (250, OnError(ex)),
      ],
      "dematerialize should call appropriate functions"
    )

  def test_distinct_until_changed(self):
    sched, xs, messages = self.simpleHot(1, 2, 2, 3, 2)

    o = sched.start(
      lambda: xs.distinctUntilChanged()
    )

    self.assertHasValues(o, [
        (210, 1),
        (220, 2),
        (240, 3),
        (250, 2),
      ],
      260,
      "distinctUntilChanged should never yield consecutive duplicate values"
    )

  def test_do(self):
    sched, xs, messages = self.simpleHot(1)
    state = Struct(
      onNextCalled=False,
      onNextValue=None,
      onCompletedCalled=False
    )

    def onNext(value):
      state.onNextCalled = True
      state.onNextValue = value

    def onCompleted():
      state.onCompletedCalled = True

    sched.start(
      lambda: xs.do(onNext, onCompleted=onCompleted)
    )

    self.assertTrue(state.onNextCalled, "do should call onNext method")
    self.assertEqual(1, state.onNextValue, "do should call onNext with correct value")
    self.assertTrue(state.onCompletedCalled, "do should call onCompleted method")

  def test_do_finally_complete(self):
    sched = TestScheduler()
    state = Struct(doCalled=False)

    def fin():
      state.doCalled = True

    sched.start(
      lambda: Observable.empty().doFinally(fin)
    )

    self.assertTrue(state.doCalled, "doFinally should call final action")

  def test_do_finally_exception(self):
    sched = TestScheduler()
    state = Struct(doCalled=False)

    def fin():
      state.doCalled = True

    sched.start(
      lambda: Observable.throw(Exception("Test Exception")).doFinally(fin)
    )

    self.assertTrue(state.doCalled, "doFinally should call final action")

  def test_ignore_elements(self):
    sched, xs, messages = self.simpleHot(1, 2, 3)

    o = sched.start(
      lambda: xs.ignoreElements()
    )

    self.assertHasValues(o, [
      ],
      240,
      "ignoreElements should ignore all elements"
    )

  def test_materialize(self):
    sched, xs, messages = self.simpleHot(1, 2, 3)

    o = sched.start(
      lambda: xs.materialize()
    )

    self.assertHasValues(o, [
        (210, OnNext(1)),
        (220, OnNext(2)),
        (230, OnNext(3)),
        (240, OnCompleted()),
      ],
      240,
      "materialize should transform values into notifications"
    )

  def test_repeat_self(self):
    sched, xs, messages = self.simpleCold(1)

    o = sched.start(
      lambda: xs.repeatSelf(2)
    )

    self.assertHasValues(o, [
        (210, 1),
        (230, 1),
      ],
      240,
      "repeatSelf should repeat itself"
    )

  def test_retry(self):
    sched = TestScheduler()
    state = Struct(count=4)

    def subscribe(observer):
      state.count -= 1

      if state.count == 0:
        observer.onNext(5)
        observer.onCompleted()
      else:
        observer.onError(Exception("Test Exception"))

    o = sched.start(
      lambda: Observable.create(subscribe).retry()
    )

    self.assertHasValues(o, [
        (200, 5),
      ],
      200,
      "repeatSelf should repeat itself"
    )

  def test_scan(self):
    sched, xs, messages = self.simpleHot(1, 2, 3)

    o = sched.start(
      lambda: xs.scan(0, lambda acc, x: acc + x)
    )

    self.assertHasValues(o, [
        (210, 1),
        (220, 3),
        (230, 6),
      ],
      240,
      "scan should yield intermediate result of accumulator on every value"
    )

  def test_skip_last(self):
    sched, xs, messages = self.simpleHot(1, 2, 3, 4, 5, 6)

    o = sched.start(
      lambda: xs.skipLast(2)
    )

    self.assertHasValues(o, [
        (230, 1),
        (240, 2),
        (250, 3),
        (260, 4),
      ],
      270,
      "skipLast should yield old values as soon as more than 'count' values have arrived"
    )

  def test_start_with(self):
    sched, xs, messages = self.simpleHot(1, 2, 3)

    o = sched.start(
      lambda: xs.startWith(5, 6)
    )

    self.assertHasValues(o, [
        (200, 5),
        (200, 6),
        (210, 1),
        (220, 2),
        (230, 3),
      ],
      240,
      "startWith should yield values at subscription, then subscribe to the original observable"
    )

  def test_take_last(self):
    sched, xs, messages = self.simpleHot(1, 2, 3, 4, 5, 6)

    o = sched.start(
      lambda: xs.takeLast(2)
    )

    self.assertHasValues(o, [
        (270, 5),
        (270, 6),
      ],
      270,
      "takeLast should yield last 'count' values"
    )

  def test_take_last_buffer(self):
    sched, xs, messages = self.simpleHot(1, 2, 3, 4, 5, 6)

    o = sched.start(
      lambda: xs.takeLastBuffer(2)
    )

    self.assertHasValues(o, [
        (270, [5, 6]),
      ],
      270,
      "takeLastBuffer should yield last 'count' values as list"
    )

  def test_window(self):
    sched, xs, messages = self.simpleHot(1, 2, 3)

    o = sched.start(
      lambda: xs.window(2, 1).selectMany(
        lambda window: window.toList()
      )
    )

    self.assertHasValues(o, [
        (220, [1, 2]),
        (230, [2, 3]),
        (240, [3]),
        (240, []),
      ],
      240,
      "window should yield windows of size at max 'count'"
    )


class TestStandardSequence(ReactiveTest):
  def test_default_if_empty(self):
    sched = TestScheduler()

    o = sched.start(
      lambda: Observable.empty().defaultIfEmpty(5)
    )

    self.assertHasValues(o, [
        (200, 5),
      ],
      200,
      "defaultIfEmpty should yield default value on empty"
    )

  def test_distinct(self):
    sched, xs, messages = self.simpleHot(1, 1, 2, 1)

    o = sched.start(
      lambda: xs.distinct()
    )

    self.assertHasValues(o, [
        (210, 1),
        (230, 2),
      ],
      250,
      "defaultIfEmpty should yield default value on empty"
    )

  def test_group_by(self):
    sched, xs, messages = self.simpleHot(
      {'k': 1, 'v': 1},
      {'k': 1, 'v': 2},
      {'k': 2, 'v': 3}
    )

    o = sched.start(
      lambda: xs.groupBy(
        lambda x: x['k'],
        lambda x: x['v']
      ).selectMany(
        lambda subject: subject.toList().select(
          lambda values: {'k': subject.key, 'v': values}
        )
      )
    )

    self.assertHasValues(o, [
        (240, {'k': 1, 'v': [1, 2]}),
        (240, {'k': 2, 'v': [3]})
      ],
      240,
      "groupBy should group values"
    )

  def test_group_by_until(self):
    sched, xs, messages = self.simpleHot(
      {'k': 1, 'v': 1},
      {'k': 1, 'v': 2},
      {'k': 2, 'v': 3}
    )

    o = sched.start(
      lambda: xs.groupByUntil(
        lambda x: x['k'],
        lambda x: x['v'],
        lambda x: Observable.never()
      ).selectMany(
        lambda subject: subject.toList().select(
          lambda values: {'k': subject.key, 'v': values}
        )
      )
    )

    self.assertHasValues(o, [
        (240, {'k': 1, 'v': [1, 2]}),
        (240, {'k': 2, 'v': [3]})
      ],
      240,
      "groupByUntil should group values"
    )

  def test_group_join(self):
    sched = TestScheduler()
    o1 = sched.createHotObservable(
      (210, OnNext(1)),
      (240, OnNext(2)),
      (250, OnCompleted())
    )
    o2 = sched.createHotObservable(
      (220, OnNext(6)),
      (230, OnNext(7)),
      (240, OnCompleted())
    )

    o = sched.start(
      lambda: o1.groupJoin(
        o2,
        lambda x: Observable.never(),
        lambda x: Observable.never(),
        lambda leftValue, leftWindow: leftWindow.select(lambda x: (leftValue, x))
      ).merge()
    )

    self.assertHasValues(o, [
        (220, (1, 6)),
        (230, (1, 7)),
        (240, (2, 6)),
        (240, (2, 7)),
      ],
      None,
      "groupJoin should yield tuples according to selector function"
    )

  def test_join(self):
    sched = TestScheduler()
    o1 = sched.createHotObservable(
      (210, OnNext(1)),
      (240, OnNext(2)),
      (250, OnCompleted())
    )
    o2 = sched.createHotObservable(
      (220, OnNext(6)),
      (230, OnNext(7)),
      (240, OnCompleted())
    )

    o = sched.start(
      lambda: o1.join(
        o2,
        lambda x: Observable.never(),
        lambda x: Observable.never(),
        lambda left, right: (left, right)
      )
    )

    self.assertHasValues(o, [
        (220, (1, 6)),
        (230, (1, 7)),
        (240, (2, 6)),
        (240, (2, 7)),
      ],
      250,
      "groupJoin should yield tuples according to selector function"
    )

  def test_of_type(self):
    sched = TestScheduler()
    xs = sched.createHotObservable(
      (210, OnNext(1)),
      (240, OnNext("Hello")),
      (250, OnCompleted())
    )

    o = sched.start(
      lambda: xs.ofType(int)
    )

    self.assertHasValues(o, [
        (210, 1),
      ],
      250,
      "ofType should ignore values that are of wrong type"
    )

  def test_select(self):
    sched, xs, messages = self.simpleHot(1, 2, 3)

    o = sched.start(
      lambda: xs.select(lambda x: x * x)
    )

    self.assertHasValues(o, [
        (210, 1),
        (220, 4),
        (230, 9),
      ],
      240,
      "select should yield selector applied to values"
    )

  def test_select_enumerate(self):
    sched, xs, messages = self.simpleHot(1, 2, 3)

    o = sched.start(
      lambda: xs.selectEnumerate(lambda x, i: x * i)
    )

    self.assertHasValues(o, [
        (210, 0),
        (220, 2),
        (230, 6),
      ],
      240,
      "selectEnumerate should yield selector applied to values"
    )

  def test_select_many(self):
    ex = Exception("Test Exception")
    sched = TestScheduler()
    xs = sched.createHotObservable(
      (210, OnNext(2)),
      (250, OnError(ex))
    )

    o = sched.start(
      lambda: xs.selectMany(
        lambda x: Observable.returnValue(x*x),
        lambda e: Observable.throw(e)
      )
    )

    self.assertHasRecorded(o, [
        (210, OnNext(4)),
        (250, OnError(ex)),
      ],
      "selectMany should subscribe to the observable returned by the selector"
    )

  def test_select_many_ignore(self):
    ex = Exception("Test Exception")
    sched = TestScheduler()
    xs = sched.createHotObservable(
      (210, OnNext(2)),
      (250, OnError(ex))
    )

    o = sched.start(
      lambda: xs.selectMany(
        Observable.returnValue(1234)
      )
    )

    self.assertHasRecorded(o, [
        (210, OnNext(1234)),
        (250, OnError(ex)),
      ],
      "selectMany should subscribe to the observable given as parameter"
    )

  def test_skip(self):
    sched, xs, messages = self.simpleHot(1, 2, 3, 4)

    o = sched.start(
      lambda: xs.skip(3)
    )

    self.assertHasValues(o, [
        (240, 4),
      ],
      250,
      "skip should skip 'count' values"
    )

  def test_skip_while(self):
    sched, xs, messages = self.simpleHot(1, 2, 4, 1)

    o = sched.start(
      lambda: xs.skipWhile(lambda x: x < 4)
    )

    self.assertHasValues(o, [
        (230, 4),
        (240, 1),
      ],
      250,
      "skipWhile should skip values as long as predicate returns True"
    )

  def test_skip_while_enumerate(self):
    sched, xs, messages = self.simpleHot(1, 2, 4, 1)

    o = sched.start(
      lambda: xs.skipWhileEnumerate(lambda x, i: i < 2)
    )

    self.assertHasValues(o, [
        (230, 4),
        (240, 1),
      ],
      250,
      "skipWhileEnumerate should skip values as long as predicate returns True"
    )

  def test_take(self):
    sched, xs, messages = self.simpleHot(1, 2, 3, 4)

    o = sched.start(
      lambda: xs.take(3)
    )

    self.assertHasValues(o, [
        (210, 1),
        (220, 2),
        (230, 3),
      ],
      230,
      "take should yield 'count' values"
    )

  def test_take_while(self):
    sched, xs, messages = self.simpleHot(1, 2, 3, 4)

    o = sched.start(
      lambda: xs.takeWhile(lambda x: x < 4)
    )

    self.assertHasValues(o, [
        (210, 1),
        (220, 2),
        (230, 3),
      ],
      240,
      "takeWhile should yield values as long predicate returns True"
    )

  def test_take_while_enumerate(self):
    sched, xs, messages = self.simpleHot(1, 2, 3, 4)

    o = sched.start(
      lambda: xs.takeWhileEnumerate(lambda x, i: i < 3)
    )

    self.assertHasValues(o, [
        (210, 1),
        (220, 2),
        (230, 3),
      ],
      240,
      "takeWhileEnumerate should yield values as long predicate returns True"
    )

  def test_where(self):
    sched, xs, messages = self.simpleHot(1, 2, 3, 2)

    o = sched.start(
      lambda: xs.where(lambda x: x < 3)
    )

    self.assertHasValues(o, [
        (210, 1),
        (220, 2),
        (240, 2),
      ],
      250,
      "where should yield values as long predicate returns True"
    )


class TestTime(ReactiveTest):
  def test_buffer_with_time(self):
    sched = TestScheduler()

    o = sched.createHotObservable(
      (190, OnNext(1)),
      (210, OnNext(2)),
      (220, OnNext(3)),
      (230, OnNext(4)),
      (240, OnCompleted())
    )

    observer = sched.start(lambda: o.bufferWithTime(20, 10, sched))

    self.assertHasValues(
      observer, [
        (220, [2, 3]),
        (230, [3, 4]),
        (240, [4]),
        (240, [])
      ],
      240,
      "bufferWithTime should buffer correctly"
    )









    # import pdb; pdb.set_trace()
    # import sys; sys.stdout.write(observer)



if __name__ == '__main__':
    unittest.main()