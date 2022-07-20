from abc import ABC, abstractmethod

class UndoManagerObserver(ABC):
  
  @abstractmethod
  def updateActionStack(self):
    pass