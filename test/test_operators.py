import unittest
    # sys.stdout.write(str(dir(a)))
# from rx.linq import Observable
from rx.disposable import Disposable
from rx.internal import Struct
from rx.observable import Observable
from rx.scheduler import Scheduler
from rx.subject import Subject

from test.reactive import OnNext, OnError, OnCompleted, TestObserver, TestScheduler, ReactiveTest

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
    self.assertHasMessages(
      Observable.empty(),
      OnCompleted()
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
      OnCompleted()
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
      OnCompleted()
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
      OnCompleted()
    )

  def test_iterable_for(self):
    self.assertHasMessages(
      Observable.iterableFor(range(1, 5), lambda x: Observable.returnValue(x)),
      OnNext(1),
      OnNext(2),
      OnNext(3),
      OnNext(4),
      OnCompleted()
    )

  def test_branch(self):
    def condition():
      return False

    thenSource = Observable.returnValue(5)
    elseSource = Observable.returnValue(6)

    self.assertHasMessages(
      Observable.branch(condition, thenSource, elseSource),
      OnNext(6),
      OnCompleted()
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
      OnCompleted()
    )


class TestMultiple(ReactiveTest):
  def test_amb(self):
    s1 = Subject()
    s2 = Subject()

    r = TestObserver(s1.amb(s2))

    with r.subscribe():
      s1.onNext(4)
      s2.onNext(5)
      s1.onNext(6)
      s1.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(4),
      OnNext(6),
      OnCompleted()
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
    r = TestObserver(s.catchException(handler))

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
      OnCompleted()
    )

  def test_combine_latest(self):
    s1 = Subject()
    s2 = Subject()

    o = Observable.combineLatest(s1, s2)
    r = TestObserver(o)

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
      OnCompleted()
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
      OnCompleted()
    )

    self.assertHasMessages(
      o1.concat([o2, o3]),
      OnNext(4),
      OnNext(5),
      OnNext(6),
      OnCompleted()
    )

    self.assertHasMessages(
      Observable.concat(o1, o2, o3),
      OnNext(4),
      OnNext(5),
      OnNext(6),
      OnCompleted()
    )

    self.assertHasMessages(
      Observable.concat([o1, o2, o3]),
      OnNext(4),
      OnNext(5),
      OnNext(6),
      OnCompleted()
    )

  def test_merge(self):
    s1 = Subject()
    s2 = Subject()

    r = TestObserver(Observable.merge(Observable.fromIterable([s1, s2])))

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
      OnCompleted()
    )

  def test_on_error_resume_next(self):
    ex = Exception("Test Exception")
    os = [
      Observable.throw(ex),
      Observable.throw(ex),
      Observable.throw(ex),
      Observable.returnValue(4),
    ]

    r = TestObserver(Observable.onErrorResumeNext(os))

    with r.subscribe():
      pass

    self.assertHasMessages(
      r,
      OnNext(4),
      OnCompleted()
    )

  def test_skip_until(self):
    s1 = Subject()
    s2 = Subject()

    r = TestObserver(s1.skipUntil(s2))

    with r.subscribe():
      s1.onNext(1)
      s2.onNext(3)
      s1.onNext(2)
      s1.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(2),
      OnCompleted()
    )

  def test_switch(self):
    s = Subject()
    s1 = Subject()
    s2 = Subject()

    r = TestObserver(s.switch())

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
      OnCompleted()
    )

  def test_take_until(self):
    s1 = Subject()
    s2 = Subject()

    r = TestObserver(s1.takeUntil(s2))

    with r.subscribe():
      s1.onNext(1)
      s2.onNext(3)
      s1.onNext(2)
      s1.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(1),
      OnCompleted()
    )

  def test_zip(self):
    o1 = Observable.fromIterable([1, 2])
    o2 = Observable.fromIterable([1, 2, 3])

    r = TestObserver(Observable.zip(o1, o2))

    with r.subscribe():
      pass

    self.assertHasMessages(
      r,
      OnNext((1, 1)),
      OnNext((2, 2)),
      OnCompleted()
    )


class TestSingle(ReactiveTest):
  def test_as_observable(self):
    s = Subject()

    r = TestObserver(s.asObservable())

    with r.subscribe():
      s.onNext(4)
      s.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(4),
      OnCompleted()
    )

  def test_buffer(self):
    s = Subject()
    r = TestObserver(s.buffer(2))

    with r.subscribe():
      s.onNext(1)
      s.onNext(2)
      s.onNext(3)
      s.onCompleted()

    self.assertHasMessages(
      r,
      OnNext([1, 2]),
      OnNext([3]),
      OnCompleted()
    )

  def test_dematerialize(self):
    ex = Exception("Test Exception")

    o = Observable.fromIterable([
      OnNext(4),
      OnError(ex)
    ])

    r = TestObserver(o.dematerialize())

    with r.subscribe():
      pass

    self.assertHasMessages(
      r,
      OnNext(4),
      OnError(ex)
    )

  def test_distinct_until_changed(self):
    s = Subject()
    r = TestObserver(s.distinctUntilChanged())

    with r.subscribe():
      s.onNext(4)
      s.onNext(4)
      s.onNext(5)
      s.onNext(4)
      s.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(4),
      OnNext(5),
      OnNext(4),
      OnCompleted()
    )

  def test_do(self):
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

    o = Observable.returnValue(5)
    r = TestObserver(o.do(onNext, onCompleted=onCompleted))

    with r.subscribe():
      pass

    self.assertTrue(state.onNextCalled, "do should call onNext method")
    self.assertEqual(5, state.onNextValue, "do should call onNext with correct value")
    self.assertTrue(state.onCompletedCalled, "do should call onCompleted method")

  def test_do_finally(self):
    state = Struct(count=0)

    def fin():
      state.count += 1

    r1 = TestObserver(Observable.returnValue(4).doFinally(fin))
    r2 = TestObserver(Observable.throw(Exception("Test Exception")).doFinally(fin))

    with r1.subscribe():
      pass

    with r2.subscribe():
      pass

    self.assertEqual(2, state.count, "doFinally should call final action")

  def test_ignore_elements(self):
    s = Subject()
    r = TestObserver(s.ignoreElements())

    with r.subscribe():
      s.onNext(4)
      s.onCompleted()

    self.assertHasMessages(
      r,
      OnCompleted()
    )

  def test_materialize(self):
    s = Subject()
    r = TestObserver(s.materialize())

    with r.subscribe():
      s.onNext(5)
      s.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(OnNext(5)),
      OnNext(OnCompleted()),
      OnCompleted()
    )

  def test_repeat_self(self):
    o = Observable.returnValue(4)
    r = TestObserver(o.repeatSelf(2))

    with r.subscribe():
      pass

    self.assertHasMessages(
      r,
      OnNext(4),
      OnNext(4),
      OnCompleted()
    )

  def test_retry(self):
    state = Struct(count=4)

    def subscribe(observer):
      state.count -= 1

      if state.count == 0:
        observer.onNext(5)
        observer.onCompleted()
      else:
        observer.onError(Exception("Test Exception"))

    r = TestObserver(Observable.create(subscribe).retry())

    with r.subscribe():
      pass

    self.assertHasMessages(
      r,
      OnNext(5),
      OnCompleted()
    )

  def test_scan(self):
    s = Subject()
    r = TestObserver(s.scan(0, lambda acc, x: acc + x))

    with r.subscribe():
      s.onNext(1)
      s.onNext(2)
      s.onNext(3)
      s.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(1),
      OnNext(3),
      OnNext(6),
      OnCompleted()
    )

  def test_skip_last(self):
    s = Subject()
    r = TestObserver(s.skipLast(2))

    with r.subscribe():
      s.onNext(1)
      s.onNext(2)
      s.onNext(3)
      s.onNext(4)
      s.onNext(5)
      s.onNext(6)
      s.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(1),
      OnNext(2),
      OnNext(3),
      OnNext(4),
      OnCompleted()
    )

  def test_start_with(self):
    s = Subject()
    r = TestObserver(s.startWith(1, 2))

    with r.subscribe():
      s.onNext(5)
      s.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(1),
      OnNext(2),
      OnNext(5),
      OnCompleted()
    )

  def test_take_last(self):
    s = Subject()
    r = TestObserver(s.takeLast(2))

    with r.subscribe():
      s.onNext(1)
      s.onNext(2)
      s.onNext(3)
      s.onNext(4)
      s.onNext(5)
      s.onNext(6)
      s.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(5),
      OnNext(6),
      OnCompleted()
    )

  def test_take_last_buffer(self):
    s = Subject()
    r = TestObserver(s.takeLastBuffer(2))

    with r.subscribe():
      s.onNext(3)
      s.onNext(4)
      s.onNext(5)
      s.onNext(6)
      s.onCompleted()

    self.assertHasMessages(
      r,
      OnNext([5, 6]),
      OnCompleted()
    )

  def test_window(self):
    s1 = Subject()
    s2 = Subject()
    r = TestObserver(s2)

    s1.window(2, 1).subscribe(
      lambda x: x.toList().subscribe(s2.onNext),
      s2.onError,
      s2.onCompleted
    )

    with r.subscribe():
      s1.onNext(3)
      s1.onNext(4)
      s1.onNext(5)
      s1.onCompleted()

    self.assertHasMessages(
      r,
      OnNext([3, 4]),
      OnNext([4, 5]),
      OnNext([5]),
      OnNext([]),
      OnCompleted()
    )


class TestStandardSequence(ReactiveTest):
  def test_default_if_empty(self):
    s = Subject()
    r = TestObserver(s.defaultIfEmpty(5))

    with r.subscribe():
      s.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(5),
      OnCompleted()
    )

  def test_distinct(self):
    s = Subject()
    r = TestObserver(s.distinct())

    with r.subscribe():
      s.onNext(4)
      s.onNext(4)
      s.onNext(5)
      s.onNext(4)
      s.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(4),
      OnNext(5),
      OnCompleted()
    )

  def test_group_by(self):
    s1 = Subject()
    s2 = Subject()
    r = TestObserver(s2)

    s1.groupBy(
      lambda x: x['k'], lambda x: x['v']
    ).subscribe(
      lambda subject: subject.toList().subscribe(
        lambda values: s2.onNext({'k': subject.key, 'v': values})
      ),
      s2.onError,
      s2.onCompleted
    )

    with r.subscribe():
      s1.onNext({'k': 1, 'v': 1})
      s1.onNext({'k': 1, 'v': 2})
      s1.onNext({'k': 2, 'v': 3})
      s1.onCompleted()

    self.assertHasMessages(
      r,
      OnNext({'k': 1, 'v': [1, 2]}),
      OnNext({'k': 2, 'v': [3]}),
      OnCompleted()
    )

  def test_group_by_until(self):
    s1 = Subject()
    s2 = Subject()
    r = TestObserver(s2)

    s1.groupByUntil(
      lambda x: x['k'],
      lambda x: x['v'],
      lambda x: Observable.never()
    ).subscribe(
      lambda obs: obs.toList().subscribe(
        lambda values: s2.onNext({'k': obs.key, 'v': values})
      ),
      s2.onError,
      s2.onCompleted
    )

    with r.subscribe():
      s1.onNext({'k': 1, 'v': 1})
      s1.onNext({'k': 1, 'v': 2})
      s1.onNext({'k': 2, 'v': 3})
      s1.onCompleted()

    self.assertHasMessages(
      r,
      OnNext({'k': 1, 'v': [1, 2]}),
      OnNext({'k': 2, 'v': [3]}),
      OnCompleted()
    )

  def test_group_join(self):
    s1 = Subject()
    s2 = Subject()
    s3 = Subject()

    s1.groupJoin(
      s2,
      lambda x: Observable.never(),
      lambda x: Observable.never(),
      lambda leftValue, rightObs: rightObs.select(lambda x: (leftValue, x))
    ).subscribe(
      lambda x: x.subscribe(s3.onNext),
      s3.onError,
      s3.onCompleted
    )

    r = TestObserver(s3)

    with r.subscribe():
      s1.onNext(1)
      s2.onNext(5)
      s1.onNext(2)
      s1.onCompleted()
      s2.onCompleted()

    self.assertHasMessages(
      r,
      OnNext((1, 5)),
      OnNext((2, 5)),
      OnCompleted()
    )

  def test_join(self):
    s1 = Subject()
    s2 = Subject()

    o = s1.join(
      s2,
      lambda x: Observable.never(),
      lambda x: Observable.never(),
      lambda left, right: (left, right)
    )

    r = TestObserver(o)

    with r.subscribe():
      s1.onNext(1)
      s2.onNext(5)
      s1.onNext(2)
      s1.onCompleted()
      s2.onCompleted()

    self.assertHasMessages(
      r,
      OnNext((1, 5)),
      OnNext((2, 5)),
      OnCompleted()
    )

  def test_of_type(self):
    s = Subject()
    r = TestObserver(s.ofType(int))

    with r.subscribe():
      s.onNext("Hello")
      s.onNext(4)
      s.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(4),
      OnCompleted()
    )

  def test_select(self):
    s = Subject()
    r = TestObserver(s.select(lambda x: x * x))

    with r.subscribe():
      s.onNext(2)
      s.onNext(4)
      s.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(4),
      OnNext(16),
      OnCompleted()
    )

  def test_select_enumerate(self):
    s = Subject()
    r = TestObserver(s.selectEnumerate(lambda x, i: x * i))

    with r.subscribe():
      s.onNext(2)
      s.onNext(4)
      s.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(0),
      OnNext(4),
      OnCompleted()
    )

  def test_select_many(self):
    ex = Exception("Test Exception")
    s = Subject()
    r = TestObserver(s.selectMany(
      lambda x: Observable.returnValue(x*x),
      lambda ex: Observable.throw(ex)
    ))

    with r.subscribe():
      s.onNext(2)
      s.onNext(4)
      s.onError(ex)

    self.assertHasMessages(
      r,
      OnNext(4),
      OnNext(16),
      OnError(ex)
    )

  def test_select_many_ignore(self):
    ex = Exception("Test Exception")
    s = Subject()
    r = TestObserver(s.selectMany(
      Observable.returnValue(1423)
    ))

    with r.subscribe():
      s.onNext(1)
      s.onNext(2)
      s.onError(ex)

    self.assertHasMessages(
      r,
      OnNext(1423),
      OnNext(1423),
      OnError(ex)
    )

  def test_skip(self):
    s = Subject()
    r = TestObserver(s.skip(3))

    with r.subscribe():
      s.onNext(1)
      s.onNext(2)
      s.onNext(3)
      s.onNext(4)
      s.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(4),
      OnCompleted()
    )

  def test_skip_while(self):
    s = Subject()
    r = TestObserver(s.skipWhile(lambda x: x < 4))

    with r.subscribe():
      s.onNext(1)
      s.onNext(2)
      s.onNext(3)
      s.onNext(4)
      s.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(4),
      OnCompleted()
    )

  def test_skip_while_enumerate(self):
    s = Subject()
    r = TestObserver(s.skipWhileEnumerate(lambda x, i: i < 3))

    with r.subscribe():
      s.onNext(1)
      s.onNext(2)
      s.onNext(3)
      s.onNext(4)
      s.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(4),
      OnCompleted()
    )

  def test_take(self):
    s = Subject()
    r = TestObserver(s.take(3))

    with r.subscribe():
      s.onNext(1)
      s.onNext(2)
      s.onNext(3)
      s.onNext(4)
      s.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(1),
      OnNext(2),
      OnNext(3),
      OnCompleted()
    )

  def test_take_while(self):
    s = Subject()
    r = TestObserver(s.takeWhile(lambda x: x < 4))

    with r.subscribe():
      s.onNext(1)
      s.onNext(2)
      s.onNext(3)
      s.onNext(4)
      s.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(1),
      OnNext(2),
      OnNext(3),
      OnCompleted()
    )

  def test_take_while_enumerate(self):
    s = Subject()
    r = TestObserver(s.takeWhileEnumerate(lambda x, i: i < 3))

    with r.subscribe():
      s.onNext(1)
      s.onNext(2)
      s.onNext(3)
      s.onNext(4)
      s.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(1),
      OnNext(2),
      OnNext(3),
      OnCompleted()
    )

  def test_where(self):
    s = Subject()
    r = TestObserver(s.where(lambda x: x < 3))

    with r.subscribe():
      s.onNext(1)
      s.onNext(90)
      s.onNext(2)
      s.onNext(80)
      s.onCompleted()

    self.assertHasMessages(
      r,
      OnNext(1),
      OnNext(2),
      OnCompleted()
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