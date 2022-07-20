from abc import ABC, abstractmethod

class ClipboardObserver(ABC):

  @abstractmethod
  def updateClipboard(self):
    pass