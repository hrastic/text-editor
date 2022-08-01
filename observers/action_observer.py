from abc import ABC, abstractmethod

class ActionObserver(ABC):

  @abstractmethod
  def updateActionObserver(self, flag):
    pass