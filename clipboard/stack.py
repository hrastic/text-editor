from typing import Any, List

class Stack:
  _elements: List[Any] = None

  def __init__(self) -> None:
    self._elements = []
  
  def push(self, element: str) -> None:
    self._elements.append(element)
  
  def pop(self) -> Any:
    return self._elements.pop()
  
  def get_text(self) -> str:
    return self._elements[-1]
  
  def pop_get_text(self) -> str:
    element = self._elements.pop()
    return element

  def isEmpty(self) -> bool:
    return not bool(self._elements)
  
  def clear(self) -> None:
    self._elements = []