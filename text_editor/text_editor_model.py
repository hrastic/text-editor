from calendar import c
from typing import List
from collections.abc import Iterator

from location.location import Location
from location.location_range import LocationRange
from iteratori.iteratori import IteratorAllLines, IteratorLinesRange

from observers.text_observer import TextObserver
from observers.cursor_observer import CursorObserver

from actions.edit_action import EditAction
from undo.undo_manager import UndoManager

class DeleteAfterAction(EditAction):
  """Implementacija komande za brisanje znaka prije kursora"""
  _model: 'TextEditorModel' = None
  _previousStateOfLines: List[str] = []
  _previousCursorLocation: Location = None

  def __init__(self, model: 'TextEditorModel') -> None:
    self._model = model

  def executeDo(self) -> None:
    """
    Provjerava je li kursor nakon zadnjeg slova u retku. Ako je, 
    tada samo prispoji sljedeći redak ka trenutnom. Inače, briše znak
    prije kursora i pomakne kursor ulijevo.
    """
    lines = self._model.lines
    cursorLocation = self._model.cursorLocation

    self._previousStateOfLines = list(lines)
    self._previousCursorLocation = Location(cursorLocation.x, cursorLocation.y)

    length_of_current_line = len(lines[cursorLocation.y])
    number_of_lines = len(lines) - 1

    if cursorLocation.x == length_of_current_line:
      if cursorLocation.y != number_of_lines:
        lines[cursorLocation.y] += lines[cursorLocation.y + 1]
        lines.remove(lines[cursorLocation.y+1])
      else:
        return
    else:
      lines[cursorLocation.y] = lines[cursorLocation.y][0:cursorLocation.x] + lines[cursorLocation.y][cursorLocation.x+1:]
    
    
    self._model.notifyTextObservers()

  
  def executeUndo(self) -> None:
    self._model.lines = self._previousStateOfLines
    self._model.cursorLocation = self._previousCursorLocation

    self._model.notifyTextObservers()
    self._model.notifyCursorObservers()


class DeleteBeforeAction(EditAction):
  """Implementacija komande za brisanje znaka nakon kursora."""
  _model: 'TextEditorModel' = None
  _previousStateOfLines: List[str] = []
  _previousCursorLocation: Location = None

  def __init__(self, model: 'TextEditorModel') -> None:
    self._model = model

  def executeDo(self) -> None:
    lines = self._model.lines
    cursorLocation = self._model.cursorLocation

    self._previousStateOfLines = list(lines)
    self._previousCursorLocation = Location(cursorLocation.x, cursorLocation.y)

    if cursorLocation.x == 0:
      if cursorLocation.y != 0:
        lines[cursorLocation.y - 1] += lines[cursorLocation.y]
        lines.remove(lines[cursorLocation.y])
      else:
        return
    else:
      lines[cursorLocation.y] = lines[cursorLocation.y][0:cursorLocation.x-1] + lines[cursorLocation.y][cursorLocation.x:]
    
    self._model.moveCursorLeft()
    self._model.notifyTextObservers()

  def executeUndo(self) -> None:
    self._model.lines = self._previousStateOfLines
    self._model.cursorLocation = self._previousCursorLocation

    self._model.notifyTextObservers()
    self._model.notifyCursorObservers()


class DeleteRangeAction(EditAction):
  """Implementacija komande za brisanje raspona znakova."""
  _model: 'TextEditorModel' = None
  _previousStateOfLines: List[str] = []
  _previousCursorLocation: Location = None
  _previousSelectionRange: LocationRange = None

  def __init__(self, model: 'TextEditorModel') -> None:
    self._model = model
  
  def executeDo(self) -> None:
    lines = self._model.lines
    cursorLocation = self._model.cursorLocation
    selectionRange = self._model.selectionRange

    self._previousStateOfLines = list(lines)
    self._previousCursorLocation = Location(cursorLocation.x, cursorLocation.y)
    self._previousSelectionRange = selectionRange

    lines[selectionRange.start.y] = lines[selectionRange.start.y][0:selectionRange.start.x] + lines[selectionRange.start.y][selectionRange.end.x:]
    cursorLocation.setLocation(selectionRange.start.x, selectionRange.start.y)

    self._model.clearSelection()
    self._model.notifyCursorObservers()
  
  def executeUndo(self) -> None:
    self._model.lines = self._previousStateOfLines
    self._model.cursorLocation = self._previousCursorLocation
    self._model.selectionRange = self._previousSelectionRange

    self._model.notifyTextObservers()
    self._model.notifyCursorObservers()


class InsertAction(EditAction):
  """Implementacija komande za ubacivanje jednog ili više znakova."""
  _model: 'TextEditorModel' = None
  _previousStateOfLines: List[str] = []
  _previousCursorLocation: Location = None
  _previousSelectionRange: LocationRange = None

  def __init__(self, model: 'TextEditorModel', c:str) -> None:
    self._model = model
    self._c = c
  
  def executeDo(self) -> None:
    lines = self._model.lines
    cursorLocation = self._model.cursorLocation
    selectionRange = self._model.selectionRange

    self._previousStateOfLines = list(lines)
    self._previousCursorLocation = Location(cursorLocation.x, cursorLocation.y)
    self._previousSelectionRange = selectionRange

    if selectionRange:
      self._model.deleteRange()
    
    if self._c == 'Return':
      previous_line = lines[cursorLocation.y][:cursorLocation.x]
      next_line = lines[cursorLocation.y][cursorLocation.x:]
      lines[cursorLocation.y] = previous_line
      lines[cursorLocation.y+1:] = next_line, *lines[cursorLocation.y+1:]

    else:
      lines[cursorLocation.y] = lines[cursorLocation.y][:cursorLocation.x] + self._c + lines[cursorLocation.y][cursorLocation.x:]
      cursorLocation.update(len(self._c), 0)
    
    self._model.notifyTextObservers()
    self._model.notifyCursorObservers()
  
  def executeUndo(self) -> None:
    self._model.lines = self._previousStateOfLines
    self._model.cursorLocation = self._previousCursorLocation
    self._model.selectionRange = self._previousSelectionRange

    self._model.notifyTextObservers()
    self._model.notifyCursorObservers()

class TextEditorModel:
  _lines: List[str] = []
  _selectionRange: LocationRange = None
  _cursorLocation: Location = None
  _cursorObservers: List[CursorObserver] = []
  _textObservers: List[TextObserver] = []
  _undoManager: UndoManager = None

  def __init__(self, znakovni_niz: str) -> None:
    self._lines = znakovni_niz.split("\n")
    self._undoManager = UndoManager()
    self._cursorLocation = Location(0, 0)

  @property
  def lines(self) -> List[str]:
    return self._lines
  
  @property
  def selectionRange(self) -> LocationRange:
    return self._selectionRange
  
  @property
  def cursorLocation(self) -> Location:
    return self._cursorLocation
  
  @lines.setter
  def lines(self, lines: List[str]) -> None:
    self._lines = lines
  
  @selectionRange.setter
  def selectionRange(self, selectionRange: LocationRange) -> None:
    self._selectionRange = selectionRange
  
  @cursorLocation.setter
  def cursorLocation(self, cursorLocation: Location) -> None:
    self._cursorLocation = cursorLocation

  def clearSelection(self) -> None:
    self._selectionRange = None
    self.notifyTextObservers()

  def getSelectionText(self) -> str:
    return self._lines[self._selectionRange.start.y][self._selectionRange.start.x:self._selectionRange.end.x]

  def allLines(self) -> Iterator:
    """
    Vraća iterator koji iterira kroz sve retke dokumenta.
    """
    return IteratorAllLines(self._lines)
  
  def linesRange(self, index1: int, index2: int) -> Iterator:
    """
    Vraća iterator koji iterira kroz dani raspon redaka.
    
    Parametri:
      index1 (int): Od kojeg retka počinje iterator (uključiv)
      index2 (int): Do kojeg retka ide iterator (isključiv)
    """
    return IteratorLinesRange(index1, index2, self._lines)

  def attachTextObserver(self, observer: TextObserver) -> None:
    self._textObservers.append(observer)
  
  def dettachTextObserver(self, observer: TextObserver) -> None:
    self._textObservers.remove(observer)
  
  def notifyTextObservers(self) -> None:
    for observer in self._textObservers:
      observer.updateText()

  def deleteAfter(self, *args) -> None:
    """
    Briše znak nakon kursora i ne pomiče kursor.
    """
    action = DeleteAfterAction(self)
    action.executeDo()
    self._undoManager.push(action)
  
  def deleteBefore(self, *args) -> None:
    """
    Briše znak prije kursora i pomiče kursor ulijevo.
    """
    action = DeleteBeforeAction(self)
    action.executeDo()
    self._undoManager.push(action)

  def deleteRange(self, *args) -> None:
    """
    Briše trenutno označeni raspon znakova.
    """
    action = DeleteRangeAction(self)
    action.executeDo()
    self._undoManager.push(action)

  def insert(self, c: str) -> None:
    """
    Umeće se znak (ili proizvoljan tekst) na mjesto na kojem je kursor 
    i pomiče se kursor.
    """
    action = InsertAction(self, c)
    action.executeDo()
    print("PUSH")
    self._undoManager.push(action)

  def attachCursorObserver(self, observer: CursorObserver) -> None:
    self._cursorObservers.append(observer)
  
  def dettachCursorObserver(self, observer: CursorObserver) -> None:
    self._cursorObservers.remove(observer)

  def notifyCursorObservers(self) -> None:
    for observer in self._cursorObservers:
      observer.updateCursorLocation()

  def moveCursorLeft(self) -> None:
    """
    Pomiče kursor ulijevo.
    """
    if self._cursorLocation.x == 0:
      if self._cursorLocation.y != 0:
        self._cursorLocation.setLocation(len(self._lines[self._cursorLocation.y-1]), self._cursorLocation.y-1)
      else:
        return
    else:
        self._cursorLocation.update(-1, 0)
    self.notifyCursorObservers()

  def moveCursorRight(self) -> None:
    """
    Pomiče kursor udesno.
    """
    try:
      lineLength = len(self._lines[self._cursorLocation.y])
      if lineLength == self._cursorLocation.x:
        self._cursorLocation.setLocation(0, self._cursorLocation.y+1)
      else:
        self._cursorLocation.update(1, 0)
      self.notifyCursorObservers()
    except:
      pass


  def moveCursorUp(self) -> None:
    """
    Pomiče kursor gore.
    """
    if self._cursorLocation.y == 0:
      if self._cursorLocation.x != 0:

        self._cursorLocation.setLocation(0, 0)
      else:
        return
    else:
      length_current_line = len(self._lines[self._cursorLocation.y])
      length_previous_line = len(self._lines[self._cursorLocation.y - 1])
      diff = length_previous_line - length_current_line
      if self._cursorLocation.x == length_current_line and diff < 0:
        self._cursorLocation.update(diff, -1)
      else:
        self._cursorLocation.update(0, -1)
    self.notifyCursorObservers()
  
  def moveCursorDown(self) -> None:
    """
    Pomiče kursor dolje.
    """
    number_of_lines = len(self._lines)-1
    length_of_last_line = len(self._lines[number_of_lines])
    if self._cursorLocation.y == number_of_lines:
      if self._cursorLocation.x != length_of_last_line:
        self._cursorLocation.setLocation(length_of_last_line, number_of_lines)
      else:
        return
    else:
      length_current_line = len(self._lines[self._cursorLocation.y])
      length_next_line = len(self._lines[self._cursorLocation.y + 1])
      diff = length_next_line - length_current_line
      if self._cursorLocation.x == length_current_line and diff<0:
        self._cursorLocation.update(diff, 1)
      else:
        self._cursorLocation.update(0, 1)
    
    self.notifyCursorObservers()


  def moveCursorToDocumentStart(self) -> None:
    """
    Pomiče kursor na početak dokumenta.
    """
    self._cursorLocation.setLocation(0, 0)
    self.notifyCursorObservers()
  
  def moveCursorToDocumentEnd(self) -> None:
    """
    Pomiče kursor na kraj dokumenta.
    """
    number_of_lines = len(self._lines)-1
    length_of_last_line = len(self._lines[number_of_lines])
    self._cursorLocation.setLocation(length_of_last_line, number_of_lines)
    self.notifyCursorObservers()

  def addSelectionOnLeft(self) -> None:
    """
    Dodaje selekciju znakova ulijevo. Ne podržava označavanje više
    redaka teksta odjednom.
    """
    if not self._selectionRange:
      start = Location(self._cursorLocation.x-1, self._cursorLocation.y)
      end = Location(self._cursorLocation.x, self._cursorLocation.y)
      self._selectionRange = LocationRange(start, end)
    else:
      self._selectionRange.start = Location(self._cursorLocation.x-1, self._cursorLocation.y)
    self.moveCursorLeft()
    self.notifyTextObservers()
  
  def addSelectionOnRight(self) -> None:
    """
    Dodaje selekciju znakova udesno. Ne podržava označavanje više
    redaka teksta odjednom.
    """
    if not self._selectionRange:
      start = Location(self._cursorLocation.x, self._cursorLocation.y)
      end = Location(self._cursorLocation.x+1, self._cursorLocation.y)
      self._selectionRange = LocationRange(start, end)
    else:
      self._selectionRange.end = Location(self._cursorLocation.x+1, self._cursorLocation.y)
    self.moveCursorRight()
    self.notifyTextObservers()