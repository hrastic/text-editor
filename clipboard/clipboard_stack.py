from typing import List
from observers.clipboard_observer import ClipboardObserver
from clipboard.stack import Stack

class ClipboardStack:
  _clipboard_observers: List[ClipboardObserver] = []
  _texts: Stack = None

  def __init__(self) -> None:
    self._texts = Stack()
  
  def attachClipboardObserver(self, observer: ClipboardObserver) -> None:
    self._clipboard_observers.append(observer)
  
  def dettachClipboardObserver(self, observer: ClipboardObserver) -> None:
    self._clipboard_observers.remove(observer)

  def notifyClipboardObservers(self) -> None:
    for observer in self._clipboard_observers:
      observer.updateClipboard()

  def push(self, text: str) -> None:
    self._texts.push(text)
    self.notifyClipboardObservers()

  def get_text(self) -> str:
    return self._texts.get_text()

  def isEmpty(self) -> bool:
    return self._texts.isEmpty()

  def pop_get_text(self) -> str:
    text = self._texts.pop_get_text()
    self.notifyClipboardObservers()
    return text