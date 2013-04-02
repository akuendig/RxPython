class InvalidOperationException(Exception):
  def __init__(self, text):
    super(InvalidOperationException, self).__init__("Invalid operation: %s" % text)


class FutureCanceledException(Exception):
  def __init__(self):
    super(FutureCanceledException, self).__init__("Future was canceled")


class DisposedException(Exception):
  def __init__(self):
    super(DisposedException, self).__init__("Object already disposed")


class TimeoutException(Exception):
  def __init__(self):
    super(TimeoutException, self).__init__("Operation timed out")
