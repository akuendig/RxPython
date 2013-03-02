from threading import RLock

class Atomic:
  def __init__(self, value=None, lock=RLock()):
    self.lock = lock
    self._value = value

  def value():
      doc = "The value property."
      def fget(self):
          return self._value
      def fset(self, value):
          self.exchange(value)
      return locals()
  value = property(**value())

  def exchange(self, value):
    with self.lock:
      old = self.value
      self.value = value
      return old

  def compareExchange(self, value, expected):
    with self.lock:
      old = self.value

      if old == expected:
        self.value = value

      return old

  def inc(self, by=1):
    with self.lock:
      self.value += by
      return self.value

  def dec(self, by=1):
    with self.lock:
      self.value -= by
      return self.value