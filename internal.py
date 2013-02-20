def noop(*args, **kwargs): pass
def defaultError(error, *args, **kwargs): raise error

def errorIfDisposed(disposable):
  if disposable.isDisposed:
    raise Exception("Object has been disposed")

class Struct:
  def __init__(self, **entries):
    self.__dict__.update(entries)
