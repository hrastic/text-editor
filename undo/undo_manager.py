from clipboard.stack import Stack
from observers.undo_manager_observer import UndoManagerObserver
from typing import List, Any

from threading import Lock

class SingletonMetaType(type):

  _instances = {}
  _lock: Lock = Lock()

  def __call__(cls, *args: Any, **kwargs: Any) -> Any:
    with cls._lock:
      if cls not in cls._instances:
        instance = super().__call__(*args, **kwargs)
        cls._instances[cls] = instance
    return cls._instances[cls]

class UndoManager(metaclass=SingletonMetaType):
  _undoStack: Stack = None
  _redoStack: Stack = None
  _undoManagerObservers: List[UndoManagerObserver] = []

  def attach(self, observer: UndoManagerObserver):
    self._undoManagerObservers.append(observer)

  def dettach(self, observer: UndoManagerObserver):
    self._undoManagerObservers.remove(observer)
  
  def notify(self):
    for observer in self._undoManagerObservers:
      observer.updateActionStack()

  def __init__(self) -> None:
    self._undoStack = Stack()
    self._redoStack = Stack()
  
  def undo(self):
    naredba = self._undoStack.pop()
    self._redoStack.push(naredba)
    naredba.executeUndo()
    self.notify()

  def redo(self):
    naredba = self._redoStack.pop()
    naredba.executeDo()
    self._undoStack.push(naredba)
    self.notify()
  
  def push(self, c):
    self._redoStack.clear()
    self._undoStack.push(c)
    self.notify()
    

