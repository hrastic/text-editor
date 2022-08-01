from abc import ABC, abstractmethod

from location.location import Location

class CursorObserver(ABC):

  @abstractmethod
  def updateCursorLocation(self, loc: Location) -> None:
    pass