from collections.abc import Iterator
from typing import List

class IteratorAllLines(Iterator):
  """
  Iterira kroz sve retke dokumenta.
  """
  _lines: List[str] = []
  _position: int = None

  def __init__(self, lines) -> None:
    self._lines = lines
    self._position = 0
  
  def __next__(self) -> str:
    try:
      value = self._lines[self._position]
      self._position += 1
    except IndexError:
      raise StopIteration()
    
    return value


class IteratorLinesRange(Iterator):
  """
  Iterira kroz dani raspon redaka (prvi uključiv, drugi isključiv).
  """

  _index1: int = None
  _index2: int = None
  _lines: List[str] = []
  _position: int = None

  def __init__(self, index1, index2, lines) -> None:
    self._index1 = index1
    self._index2 = index2
    self._lines = lines
    self._position = index1

  def __next__(self) -> str:
    if self._position >= self._index2:
      raise StopIteration()
    try:
      value = self._lines[self._position]
      self._position += 1
    except IndexError:
      raise StopIteration()
    
    return value