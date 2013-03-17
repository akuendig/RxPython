from rx.disposable import CompositeDisposable, RefCountDisposable, SingleAssignmentDisposable
from rx.observable import GroupObservable, Producer
from rx.observer import Observer
from rx.subject import Subject
from .sink import Sink
from threading import RLock


class GroupByUntil(Producer):
  def __init__(self, source, keySelector, elementSelector, durationSelector):
    self.source = source
    self.keySelector = keySelector
    self.elementSelector = elementSelector
    self.durationSelector = durationSelector

  def run(self, observer, cancel, setSink):
    self.groupDisposable = CompositeDisposable()
    self.refCountDisposable = RefCountDisposable(self.groupDisposable)

    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    self.groupDisposable.add(self.source.subscribeSafe(sink))

    return self.refCountDisposable


  class Sink(Sink):
    def __init__(self, parent, observer, cancel):
      super(GroupByUntil.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.map = {}
      self.null = None
      self.nullGate = RLock()
      self.nullGateForDeltas = RLock()
      self.observerGate = RLock()
      self.writerGate = RLock()

    def onNext(self, value):
      key = None

      try:
        key = self.parent.keySelector(value)
      except Exception as e:
        self.onError(e)
        return

      fireNewMapEntry = False
      writer = None

      try:
        if key == None:
          with self.nullGate:
            if self.null == None:
              self.null = Subject()
              fireNewMapEntry = True

            writer = self.null
        else:
          if not key in self.map:
            writer = Subject()
            self.map[key] = writer
            fireNewMapEntry = True
      except Exception as e:
        self.onError(e)
        return

      if fireNewMapEntry:
        group = GroupObservable(key, writer, self.parent.refCountDisposable)

        duration = None
        durationGroup = GroupObservable(key, writer)

        try:
          duration = self.parent.durationSelector(durationGroup)
        except Exception as e:
          self.onError(e)
          return

        with self.observerGate:
          self.observer.onNext(group)

        md = SingleAssignmentDisposable()
        self.parent.groupDisposable.add(md)
        md.disposable = duration.subscribeSafe(self.Delta(self, key, writer, md))

      element = None

      try:
        element = self.parent.elementSelector(value)
      except Exception as e:
        self.onError(e)
      else:
        with self.writerGate:
          writer.onNext(element)

    def onError(self, exception):
      #
      # NOTE: A race with OnCompleted triggered by a duration selector is fine when
      #       using Subject<T>. It will transition into a terminal state, making one
      #       of the two calls a no-op by swapping in a DoneObserver<T>.
      #
      null = None

      with self.nullGate:
        null = self.null

      if null != None:
        null.onError(exception)

      for x in self.map.values():
        x.onError(exception)

      with self.observerGate:
        self.observer.onError(exception)

      self.dispose()

    def onCompleted(self):
      #
      # NOTE: A race with OnCompleted triggered by a duration selector is fine when
      #       using Subject<T>. It will transition into a terminal state, making one
      #       of the two calls a no-op by swapping in a DoneObserver<T>.
      #
      null = None

      with self.nullGate:
        null = self.null

      if null != None:
        null.onCompleted()

      for x in self.map.values():
        x.onCompleted()

      with self.observerGate:
        self.observer.onCompleted()

      self.dispose()


    class Delta(Observer):
      def __init__(self, parent, key, writer, cancelSelf):
        self.parent = parent
        self.key = key
        self.writer = writer
        self.cancelSelf = cancelSelf

      def onNext(self, value):
        self.onCompleted()

      def onError(self, exception):
        self.parent.onError(exception)
        self.cancelSelf.dispose()

      def onCompleted(self):
        if self.key == None:
          null = None

          with self.parent.nullGate:
            null = self.parent.null
            self.parent.null = None

          with self.parent.nullGateForDeltas:
            null.onCompleted()
        else:
          try:
            del self.parent.map[self.key]
          except KeyError:
            pass
          else:
            with self.parent.writerGate:
              self.writer.onCompleted()

        self.parent.parent.groupDisposable.remove(self.cancelSelf)
    # end Delta
  #end Sink
#end GroupByUntil
