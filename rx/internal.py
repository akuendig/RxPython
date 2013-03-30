from datetime import datetime

def noop(*args, **kwargs): pass
def identity(x): return x
def defaultNow(): return datetime.now().timestamp() # UNIX time on seconds as float
def defaultComparer(x, y): return x == y
def defaultCompareTo(x, y): return 1 if x > y else -1 if x < y else 0
def defaultSubComparer(x, y): return x - y
def defaultKeySerializer(x): return str(x)
def defaultError(error, *args, **kwargs): raise error

def errorIfDisposed(disposable):
  if disposable.isDisposed:
    raise Exception("Object has been disposed")

def raiseIsDisposed(*args, **kwargs):
  raise Exception("Object has been disposed")

class Struct(object):
  def __init__(self, **entries):
    self.__dict__.update(entries)

  def __eq__(self, other):
    if not isinstance(other, Struct):
      return False

    return self.__dict__ == other.__dict__

  def __repr__(self):
    return repr(self.__dict__)
