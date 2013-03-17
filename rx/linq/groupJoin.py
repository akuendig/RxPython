from rx.disposable import CompositeDisposable, RefCountDisposable, SingleAssignmentDisposable
from rx.observable import Producer
from rx.observer import Observer
from rx.subject import Subject
from .addRef import AddRef
from .sink import Sink
from threading import RLock


class GroupJoin(Producer):
  def __init__(self, left, right, leftDurationSelector, rightDurationSelector, resultSelector):
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
      super(GroupJoin.Sink, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.gate = RLock()
      self.group = CompositeDisposable()
      self.refCount = RefCountDisposable(self.group)

      leftSubscription = SingleAssignmentDisposable()
      self.group.add(leftSubscription)
      self.leftID = 0
      self.leftMap = {}

      rightSubscription = SingleAssignmentDisposable()
      self.group.add(rightSubscription)
      self.rightID = 0
      self.rightMap = {}

      leftSubscription.disposable = self.parent.left.subscribeSafe(self.Lambda(self, leftSubscription))
      rightSubscription.disposable = self.parent.right.subscribeSafe(self.Roh(self, rightSubscription))

      return self.refCount

    class Lambda(Observer):
      def __init__(self, parent, subscription):
        self.parent = parent
        self.subscription = subscription

      def expire(self, resourceId, group, resource):
        with self.parent.gate:
          if resourceId in self.parent.leftMap:
            del self.parent.leftMap[resourceId]
            group.onCompleted()

        self.parent.group.remove(resource)

      def onNext(self, value):
        s = Subject()
        resourceId = 0

        with self.parent.gate:
          self.parent.leftID += 1
          resourceId = self.parent.leftID
          self.parent.leftMap.add(resourceId, s)

        # AddRef was originally WindowObservable but this is just an alias for AddRef
        window = AddRef(s, self.parent.refCount)
        md = SingleAssignmentDisposable()
        self.parent.group.add(md)

        try:
          duration = self.parent.parent.leftDurationSelector(value)
        except Exception as e:
          self.onError(e)
          return
        else:
          md.disposable = duration.subscribeSafe(self.Delta(self, resourceId, s, md))

        try:
          result = self.parent.parent.resultSelector(value, window)
        except Exception as e:
          self.onError(e)
          return
        else:
          with self.parent.gate:
            self.parent.observer.onNext(result)

            for rightValue in self.parent.rightMap.values():
              s.onNext(rightValue)

      def onError(self, exception):
        with self.parent.gate:
          for o in self.parent.leftMap.values():
            o.onError(exception)

          self.parent.observer.onError(exception)
          self.parent.dispose()

      def onCompleted(self):
        with self.parent.gate:
          self.parent.observer.onCompleted()
          self.parent.dispose()

        self.dispose()


      class Delta(Observer):
        """Expires parent on Next or Completed"""

        def __init__(self, parent, resourceId, group, resource):
          self.parent = parent
          self.resourceId = resourceId
          self.group = group
          self.resource = resource

        def onNext(self, value):
          self.parent.expire(self.resourceId, self.group, self.resource)

        def onError(self, exception):
          self.parent.onError(exception)

        def onCompleted(self):
          self.parent.expire(self.resourceId, self.group, self.resource)
      #end Delta
    #end Lambda

    class Roh(Observer):
      def __init__(self, parent, subscription):
        self.parent = parent
        self.subscription = subscription


      def expire(self, resourceId, resource):
        with self.parent.gate:
          self.parent.rightMap.pop(resourceId, None)

        self.parent.group.remove(resource)

      def onNext(self, value):
        resourceId = 0

        with self.parent.gate:
          self.parent.rightID += 1
          resourceId = self.parent.rightID
          self.parent.rightMap.add(resourceId, value)

        md = SingleAssignmentDisposable()
        self.parent.group.add(md)

        try:
          duration = self.parent.parent.rightDurationSelector(value)
        except Exception as e:
          self.onError(e)
          return
        else:
          md.disposable = duration.subscribeSafe(self.Delta(self, resourceId, md))

        with self.parent.gate:
          for o in self.parent.leftMap.values():
            o.onNext(value)

      def onError(self, exception):
        with self.parent.gate:
          for o in self.parent.leftMap.values():
            o.onError(exception)

          self.parent.observer.onError(exception)
          self.parent.dispose()

      def onCompleted(self):
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
    #end Roh
  #end Sink
#end GroupJoin
