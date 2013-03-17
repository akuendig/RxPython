import unittest
# import sys
# from rx.linq import Observable
from rx.observable import Observable

def rep(value, count):
  return Observable.fromIterable([value]*count)

class TestAggregation(unittest.TestCase):
  def test_aggregate(self):
    o = rep(5, 4)
    s = o.aggregate(0, lambda acc, el: acc + el).first()

    self.assertEqual(20, s, "Accumulate should yield sum")

  def test_all_true(self):
    o = rep(5, 4)
    a = o.all(lambda x: x == 5).first()

    self.assertTrue(a, "all values should be equal to 5")

  def test_any_empty(self):
    o = Observable.empty()
    a = o.any().first()

    self.assertFalse(a, "all values should not be equal to 4")

  def test_any_value(self):
    o = rep(5, 4)
    a = o.any().first()

    self.assertTrue(a, "all values should be equal to 5")

  def test_any_predicate(self):
    o = rep(5, 4)
    a = o.any(lambda x: x == 3).first()

    self.assertFalse(a, "all values should not be equal to 3")

  def test_average(self):
    o = rep(5, 4)
    a = o.average().first()

    self.assertEqual(5, a, "average sould be 5")

  def test_contains_true(self):
    o = rep(5, 4)
    a = o.contains(5).first()

    self.assertTrue(a, "should contain 5")

  def test_contains_false(self):
    o = rep(5, 4)
    a = o.contains(3).first()

    self.assertFalse(a, "should not contain 3")

  def test_count(self):
    o = rep(5, 4)
    a = o.count(lambda x: x == 5).first()

    self.assertEqual(4, a, "sequence should contain 4 elements")

  def test_first_async(self):
    o = Observable.fromIterable([3, 2, 1])
    a = o.firstAsync(lambda x: x == 2).first()

    self.assertEqual(2, a, "first 2 in sequence should be 2")


class TestAll(unittest.TestCase):

    # Only use setUp() and tearDown() if necessary

    # def setUp(self):
    #     ... code to execute in preparation for tests ...

    # def tearDown(self):
    #     ... code to execute to clean up after tests ...

    def test_build_from_iterator(self):
      # sys.stdout.write(str(dir(Observable)))
      it1 = [1, 2, 3]
      o = Observable.fromIterable(it1)
      it2 = list(o)
      self.assertSequenceEqual(it1, it2)

if __name__ == '__main__':
    unittest.main()