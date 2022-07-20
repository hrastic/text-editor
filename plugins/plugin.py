from abc import ABC, abstractmethod

class Plugin(ABC):
  
  @abstractmethod
  def getName() -> str:
    pass

  @abstractmethod
  def getDescription() -> str:
    pass

  @abstractmethod
  def execute(model, undoManager, clipboardStack) -> None:
    pass