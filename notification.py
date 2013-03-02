class Notification(object):
  """Represents a notification to an observer."""
  KIND_NEXT = 0
  KIND_ERROR = 1
  KIND_COMPLETED = 2

  @property
  def value(self):
    raise NotImplementedError()

  @property
  def hasValue(self):
    raise NotImplementedError()

  @property
  def exception(self):
    raise NotImplementedError()

  @property
  def NotificationKind(self):
    raise NotImplementedError()

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
    if hasattr(observerOrOnNext, '__call__'):
      return observerOrOnNext(self.value)
    else:
      return observerOrOnNext.onNext(self.value)


class OnErrorNotification(Notification):
  """Represents an OnNextNotification notification to an observer."""
  def __init__(self, exception):
    super(OnNextNotification, self).__init__()
    self.hasValue = False
    self.exception = exception
    self.NotificationKind = Notification.KIND_ERROR

  def accept(self, observerOrOnNext, onError=None, onCompleted=None):
    if hasattr(observerOrOnNext, '__call__'):
      return onError(self.exception)
    else:
      return observerOrOnNext.onError(self.exception)


class OnCompletedNotification(Notification):
  """Represents an OnNextNotification notification to an observer."""
  def __init__(self, value):
    super(OnNextNotification, self).__init__()
    self.hasValue = False
    self.exception = None
    self.NotificationKind = Notification.KIND_COMPLETED

  def accept(self, observerOrOnNext, onError=None, onCompleted=None):
    if hasattr(observerOrOnNext, '__call__'):
      return onCompleted()
    else:
      return observerOrOnNext.onCompleted()

