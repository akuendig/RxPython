from disposable import CompositDisposable, RefCountDisposable
from observable import GroupObservable, Producer
from subject import Subject
from .sink import Sink


class GroupBy(Producer):
  def __init__(self, source, keySelector, elementSelector):
    self.source = source
    self.keySelector = keySelector
    self.elementSelector = elementSelector

  def run(self, observer, cancel, setSink):
    self.groupDisposable = CompositDisposable()
    self.refCountDisposable = RefCountDisposable(self.groupDisposable)

    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    self.groupDisposable.add(self.source.subscribeSafe(sink))

    return self.refCountDisposable


  class Sink(Sink):
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
          if not key in self.map:
            writer = Subject()
            self.map[key] = value
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