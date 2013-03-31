class Notification(object):
  """Represents a notification to an observer."""

  KIND_NEXT = 0
  KIND_ERROR = 1
  KIND_COMPLETED = 2

  def __eq__(self, other):
    if not isinstance(other, Notification):
      return False

    return (
      self.kind == other.kind and
      self.value == other.value and
      self.hasValue == other.hasValue and
      self.exception == other.exception
    )

  def accept(self, observerOrOnNext, onError=None, onCompleted=None):
    """Accepts an observer or the methods onNext, onError, onCompleted and invokes
    either onNext, onError, onCompleted depending on which type of :class:`Notification`
    it is. This is an abstract method that is implemented by
    :class:`OnNextNotification`, :class:`OnErrorNotification`,
    and :class:`OnCompletedNotification`."""
    # if observerOrOnNext == None or hasattr(observerOrOnNext, '__call__'):
    #   observer = Observer.create(observerOrOnNext, onError, onComplete)
    raise NotImplementedError()

  @staticmethod
  def createOnNext(value):
    return OnNextNotification(value)

  @staticmethod
  def createOnError(exception):
    return OnErrorNotification(exception)

  @staticmethod
  def createOnCompleted():
    return OnCompletedNotification()


class OnNextNotification(Notification):
  """Represents an OnNextNotification notification to an observer."""
  def __init__(self, value):
    super(OnNextNotification, self).__init__()
    self.value = value
    self.hasValue = True
    self.exception = None
    self.kind = Notification.KIND_NEXT

  def __repr__(self):
    return "OnNextNotification(%s)" % repr(self.value)

  def accept(self, observerOrOnNext, onError=None, onCompleted=None):
    if callable(observerOrOnNext):
      return observerOrOnNext(self.value)
    else:
      return observerOrOnNext.onNext(self.value)


class OnErrorNotification(Notification):
  """Represents an OnNextNotification notification to an observer."""
  def __init__(self, exception):
    super(OnErrorNotification, self).__init__()
    self.value = None
    self.hasValue = False
    self.exception = exception
    self.kind = Notification.KIND_ERROR

  def __repr__(self):
    return "OnErrorNotification(%s)" % repr(self.exception)

  def accept(self, observerOrOnNext, onError=None, onCompleted=None):
    if callable(observerOrOnNext):
      return onError(self.exception)
    else:
      return observerOrOnNext.onError(self.exception)


class OnCompletedNotification(Notification):
  """Represents an OnNextNotification notification to an observer."""
  def __init__(self):
    super(OnCompletedNotification, self).__init__()
    self.value = None
    self.hasValue = False
    self.exception = None
    self.kind = Notification.KIND_COMPLETED

  def __repr__(self):
    return "OnCompletedNotification()"

  def accept(self, observerOrOnNext, onError=None, onCompleted=None):
    if callable(observerOrOnNext):
      return onCompleted()
    else:
      return observerOrOnNext.onCompleted()

