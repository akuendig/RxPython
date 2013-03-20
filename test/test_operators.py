import unittest
import sys
    # sys.stdout.write(str(dir(a)))
# from rx.linq import Observable
from rx.disposable import Disposable
from rx.internal import Struct
from rx.observable import Observable
from rx.subject import Subject

def rep(value, count):
  return Observable.fromIterable([value]*count)

class TestAggregation(unittest.TestCase):
  def test_aggregate(self):
    o = rep(5, 4)
    s = o.aggregate(0, lambda acc, el: acc + el).single()

    self.assertEqual(20, s, "Accumulate should yield sum")

  def test_all_true(self):
    o = rep(5, 4)
    a = o.all(lambda x: x == 5).single()

    self.assertTrue(a, "all values should be equal to 5")

  def test_any_empty(self):
    o = Observable.empty()
    a = o.any().single()

    self.assertFalse(a, "all values should not be equal to 4")

  def test_any_value(self):
    o = rep(5, 4)
    a = o.any().single()

    self.assertTrue(a, "all values should be equal to 5")

  def test_any_predicate(self):
    o = rep(5, 4)
    a = o.any(lambda x: x == 3).single()

    self.assertFalse(a, "all values should not be equal to 3")

  def test_average(self):
    o = rep(5, 4)
    a = o.average().single()

    self.assertEqual(5, a, "average sould be 5")

  def test_contains_true(self):
    o = rep(5, 4)
    a = o.contains(5).single()

    self.assertTrue(a, "should contain 5")

  def test_contains_false(self):
    o = rep(5, 4)
    a = o.contains(3).single()

    self.assertFalse(a, "should not contain 3")

  def test_count(self):
    o = rep(5, 4)
    a = o.count(lambda x: x == 5).single()

    self.assertEqual(4, a, "sequence should contain 4 elements")

  def test_first_async(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.firstAsync(lambda x: x == 2).single()

    self.assertEqual(2, a, "first 2 in sequence should be 2")

  def test_first_async_or_default(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.firstAsyncOrDefault(lambda x: x == 5, 7).single()

    self.assertEqual(7, a, "first 5 sould not be found, 7 sould be returned")

  def test_last_async(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.lastAsync().single()

    self.assertEqual(1, a, "last value in sequence should be 1")

  def test_last_async_or_default(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.lastAsyncOrDefault(lambda x: x == 5, 7).single()

    self.assertEqual(7, a, "last 5 sould not be found, 7 sould be returned")

  def test_max(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.max().single()

    self.assertEqual(3, a, "max value should be 3")

  def test_max_by(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.maxBy(lambda x: -x).single()

    self.assertSequenceEqual([1], a, "max inverse value should be 1")

  def test_min(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.min().single()

    self.assertEqual(1, a, "min value should be 1")

  def test_min_by(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.minBy(lambda x: -x).single()

    self.assertSequenceEqual([3], a, "min inverse value should be 3")

  def test_sequence_equal(self):
    o1 = rep(5, 4)
    o2 = rep(5, 4)
    a = o1.sequenceEqual(o2).single()

    self.assertTrue(a, "sequences should be equal")

  def test_single_async(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.singleAsync(lambda x: x == 2).single()

    self.assertEqual(2, a, "single 2 in sequence should be 2")

  def test_single_async_or_default(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.singleAsyncOrDefault(lambda x: x == 5, 7).single()

    self.assertEqual(7, a, "single 5 sould not be found, 7 sould be returned")

  def test_sum(self):
    o = rep(5, 4)
    a = o.sum().single()

    self.assertEqual(20, a, "sum should be 20")

  def test_to_list(self):
    o = rep(5, 4)
    a = o.toList().single()

    self.assertSequenceEqual([5, 5, 5, 5], a, "to list should be [5, 5, 5, 5]", list)

  def test_to_dictionary(self):
    o = Observable.fromIterable([
      ('a', 1),
      ('b', 1)
    ])
    a = o.toDictionary(lambda x: x[0], lambda x: x[1]).single()

    self.assertEqual({'a': 1, 'b': 1}, a, "dictionary should contain last values for each key")

  def test_to_dictionary_duplicate(self):
    o = Observable.fromIterable([
      ('a', 1),
      ('a', 2),
      ('b', 1)
    ])
    a = o.toDictionary(lambda x: x[0], lambda x: x[1]).single

    self.assertRaisesRegex(Exception, "Duplicate key", a)


class TestBinding(unittest.TestCase):
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


class TestBlocking(unittest.TestCase):
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
    state = Struct(
      acc=[],
      index=0
    )
    values = [3, 2, 1]

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


class TestConcurrency(unittest.TestCase):
  def test_subscribe_on(self):
    state = Struct(wasScheduled=False)

    class Sched(object):
      def schedule(self, action):
        state.wasScheduled = True

    o = Observable.fromIterable([3, 2, 1]).subscribeOn(Sched())

    with o.subscribe(lambda x: None):
      pass

    self.assertTrue(state.wasScheduled, "subscribeOn should schedule subscription on provided scheduler")

  def test_observe_on(self):
    state = Struct(loopScheduled=False)

    class Sched(object):
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


class TestCreation(unittest.TestCase):

    # Only use setUp() and tearDown() if necessary

    # def setUp(self):
    #     ... code to execute in preparation for tests ...

    # def tearDown(self):
    #     ... code to execute to clean up after tests ...

  def test_build_from_iterator(self):
    o = Observable.fromIterable([1, 2, 3])
    a1 = o.toList().wait()
    a2 = o.toList().wait()

    self.assertSequenceEqual([1, 2, 3], a1, "both should be [1, 2, 3]", list)
    self.assertSequenceEqual([1, 2, 3], a2, "both should be [1, 2, 3]", list)





    # import pdb; pdb.set_trace()
    # import sys; sys.stdout.write(observer)



if __name__ == '__main__':
    unittest.main()