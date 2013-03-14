from disposable import Disposable
from observable import Observable


class Never(Observable):
  def __init__(self):
    super(Never, self).__init__()

  def subscribeCore(self, observer):
    return Disposable.empty()