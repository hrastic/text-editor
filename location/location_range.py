from location.location import Location

class LocationRange:
  _start: Location = None
  _end: Location = None

  def __init__(self, start: Location, end: Location) -> None:
    self._start = start
    self._end = end
  
  @property
  def start(self) -> Location:
    return self._start

  @property
  def end(self) -> Location:
    return self._end

  @start.setter
  def start(self, start: Location) -> None:
    self._start = start

  @end.setter
  def end(self, end: Location) -> None:
    self._end = end

  def __str__(self) -> str:
    return f"({str(self._start)}, {str(self._end)})"