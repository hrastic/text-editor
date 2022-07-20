from abc import ABC, abstractmethod

class EditAction(ABC):
  """Interface for all actions"""

  @abstractmethod
  def executeDo(self) -> None:
    pass

  @abstractmethod
  def executeUndo(self) -> None:
    pass