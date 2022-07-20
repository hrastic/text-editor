class Location:
  _x: int = None
  _y: int = None

  def __init__(self, x: int, y: int) -> None:
    self._x = x
    self._y = y
  
  @property
  def x(self) -> int:
    return self._x
  
  @property
  def y(self) -> int:
    return self._y
  

  def setLocation(self, x: int, y: int) -> None:
    self._x = x
    self._y = y
  
  def update(self, dx: int, dy: int) -> None:
    self._x += dx
    self._y += dy
  
  def __str__(self) -> str:
    return f"({self._x},{self._y})"