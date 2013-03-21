class Notification(object):
  """Represents a notification to an observer."""
  KIND_NEXT = 0
  KIND_ERROR = 1
  KIND_COMPLETED = 2

  def __eq__(self, other):
    return (
      self.NotificationKind == other.NotificationKind and
      self.value == other.value and
      self.hasValue == other.hasValue and
      self.exception == other.exception
    )

  def accept(self, observerOrOnNext, onError=None, onCompleted=None):
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
    self.NotificationKind = Notification.KIND_NEXT

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
    self.NotificationKind = Notification.KIND_ERROR

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
    self.NotificationKind = Notification.KIND_COMPLETED

  def accept(self, observerOrOnNext, onError=None, onCompleted=None):
    if callable(observerOrOnNext):
      return onCompleted()
    else:
      return observerOrOnNext.onCompleted()

