from disposable import CompositeDisposable, RefCountDisposable, SingleAssignmentDisposable
from observable import Producer
from observer import Observer
from .sink import Sink
from threading import RLock


class Join(Producer):
  def __init__(self, left, right, leftDurationSelector, rightDurationSelector, resultSelector):
    super(Join, self).__init__()
    self.left = left
    self.right = right
    self.leftDurationSelector = leftDurationSelector
    self.rightDurationSelector = rightDurationSelector
    self.resultSelector = resultSelector


  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return sink.run()

  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(Join.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.gate = RLock()
      self.group = CompositeDisposable()
      self.refCount = RefCountDisposable(self.group)

      leftSubscription = SingleAssignmentDisposable()
      self.group.add(leftSubscription)
      self.leftDone = False
      self.leftID = 0
      self.leftMap = {}

      rightSubscription = SingleAssignmentDisposable()
      self.group.add(rightSubscription)
      self.rightDone = False
      self.rightID = 0
      self.rightMap = {}

      leftSubscription.disposable = self.parent.left.subscribeSafe(self.Lambda(self, leftSubscription))
      rightSubscription.disposable = self.parent.right.subscribeSafe(self.Roh(self, rightSubscription))

      return self.refCount

    class Lambda(Observer):
      def __init__(self, parent, subscription):
        self.parent = parent
        self.subscription = subscription

      def expire(self, resourceId, resource):
        with self.parent.gate:
          if resourceId in self.parent.leftMap:
            del self.parent.leftMap[resourceId]

            if len(self.parent.leftMap) == 0 and self.parent.leftDone:
              self.parent.observer.onCompleted()
              self.parent.dispose()

        self.parent.group.remove(resource)

      def onNext(self, value):
        resourceId = 0

        with self.parent.gate:
          self.parent.leftID += 1
          resourceId = self.parent.leftID
          self.parent.leftMap.add(resourceId, value)

        # AddRef was originally WindowObservable but this is just an alias for AddRef
        md = SingleAssignmentDisposable()
        self.parent.group.add(md)

        try:
          duration = self.parent.parent.leftDurationSelector(value)
        except Exception as e:
          self.parent.observer.onError(e)
          self.parent.dispose()
          return
        else:
          md.disposable = duration.subscribeSafe(self.Delta(self, resourceId, md))

        with self.parent.gate:
          for rightValue in self.parent.rightMap.values():
            try:
              result = self.parent.parent.resultSelector(value, rightValue)
            except Exception as e:
              self.parent.observer.onError(e)
              self.parent.dispose()
              return
            else:
              self.parent.observer.onNext(result)

      def onError(self, exception):
        with self.parent.gate:
          self.parent.observer.onError(exception)
          self.parent.dispose()

      def onCompleted(self):
        with self.parent.gate:
          self.parent.leftDone = True

          if self.parent.rightDone or len(self.parent.leftMap) == 0:
            self.parent.observer.onCompleted()
            self.parent.dispose()
          else:
            self.dispose()


      class Delta(Observer):
        """Expires parent on Next or Completed"""

        def __init__(self, parent, resourceId, resource):
          self.parent = parent
          self.resourceId = resourceId
          self.resource = resource

        def onNext(self, value):
          self.parent.expire(self.resourceId, self.resource)

        def onError(self, exception):
          self.parent.onError(exception)

        def onCompleted(self):
          self.parent.expire(self.resourceId, self.resource)
      #end Delta
    #end Lambda

    class Roh(Observer):
      def __init__(self, parent, subscription):
        self.parent = parent
        self.subscription = subscription

      def expire(self, resourceId, resource):
        with self.parent.gate:
          if resourceId in self.parent.rightMap:
            del self.parent.rightMap[resourceId]

            if len(self.parent.rightMap) == 0 and self.parent.rightDone:
              self.parent.observer.onCompleted()
              self.parent.dispose()

        self.parent.group.remove(resource)

      def onNext(self, value):
        resourceId = 0

        with self.parent.gate:
          self.parent.rightID += 1
          resourceId = self.parent.rightID
          self.parent.rightMap.add(resourceId, value)

        # AddRef was originally WindowObservable but this is just an alias for AddRef
        md = SingleAssignmentDisposable()
        self.parent.group.add(md)

        try:
          duration = self.parent.parent.rightDurationSelector(value)
        except Exception as e:
          self.parent.observer.onError(e)
          self.parent.dispose()
          return
        else:
          md.disposable = duration.subscribeSafe(self.Delta(self, resourceId, md))

        with self.parent.gate:
          for leftValue in self.parent.leftMap.values():
            try:
              result = self.parent.parent.resultSelector(leftValue, value)
            except Exception as e:
              self.parent.observer.onError(e)
              self.parent.dispose()
              return
            else:
              self.parent.observer.onNext(result)

      def onError(self, exception):
        with self.parent.gate:
          self.parent.observer.onError(exception)
          self.parent.dispose()

      def onCompleted(self):
        with self.parent.gate:
          self.parent.rightDone = True

          if self.parent.leftDone or len(self.parent.rightMap) == 0:
            self.parent.observer.onCompleted()
            self.parent.dispose()
          else:
            self.dispose()


      class Delta(Observer):
        """Expires parent on Next or Completed"""

        def __init__(self, parent, resourceId, resource):
          self.parent = parent
          self.resourceId = resourceId
          self.resource = resource

        def onNext(self, value):
          self.parent.expire(self.resourceId, self.resource)

        def onError(self, exception):
          self.parent.onError(exception)

        def onCompleted(self):
          self.parent.expire(self.resourceId, self.resource)
    #end Roh
  #end Sink
#end Join