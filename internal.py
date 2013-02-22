from datetime import datetime

def noop(*args, **kwargs): pass
def identity(x): return x
def defaultNow(): return int(datetime.now().timestamp() * 1000)
def defaultComparer(x, y): return x == y
def defaultSubComparer(x, y): return x - y
def defaultKeySerializer(x): return str(x)
def defaultError(error, *args, **kwargs): raise error

def errorIfDisposed(disposable):
  if disposable.isDisposed:
    raise Exception("Object has been disposed")

class Struct:
  def __init__(self, **entries):
    self.__dict__.update(entries)
