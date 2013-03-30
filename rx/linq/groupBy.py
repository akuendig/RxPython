from rx.disposable import CompositeDisposable, RefCountDisposable
from rx.observable import GroupObservable, Producer
from rx.subject import Subject
import rx.linq.sink


class GroupBy(Producer):
  def __init__(self, source, keySelector, elementSelector):
    self.source = source
    self.keySelector = keySelector
    self.elementSelector = elementSelector

  def run(self, observer, cancel, setSink):
    self.groupDisposable = CompositeDisposable()
    self.refCountDisposable = RefCountDisposable(self.groupDisposable)

    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    self.groupDisposable.add(self.source.subscribeSafe(sink))

    return self.refCountDisposable


  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(GroupBy.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.map = {}
      self.null = None

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
          if self.null == None:
            self.null = Subject()
            fireNewMapEntry = True

          writer = self.null
        else:
          if key in self.map:
            writer = self.map[key]
          else:
            writer = Subject()
            self.map[key] = writer
            fireNewMapEntry = True
      except Exception as e:
        self.onError(e)
        return

      if fireNewMapEntry:
        group = GroupObservable(key, writer, self.parent.refCountDisposable)
        self.observer.onNext(group)

      element = None

      try:
        element = self.parent.elementSelector(value)
      except Exception as e:
        self.onError(e)
      else:
        writer.onNext(element)

    def onError(self, exception):
      if self.null != None:
        self.null.onError(exception)

      for x in self.map.values():
        x.onError(exception)

      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      if self.null != None:
        self.null.onCompleted()

      for x in self.map.values():
        x.onCompleted()

      self.observer.onCompleted()
      self.dispose()