from tkinter import *
from tkinter import font as tkFont
from typing import List

from location.location import Location
from observers.undo_manager_observer import UndoManagerObserver
from observers.action_observer import ActionObserver

from undo.undo_manager import UndoManager

from observers.text_observer import TextObserver
from observers.cursor_observer import CursorObserver
from observers.clipboard_observer import ClipboardObserver
from text_editor.text_editor_model import TextEditorModel
from actions.action import Action
from clipboard.clipboard_stack import ClipboardStack
from observers.button_observer import ButtonObserver
from observers.edit_menu_observer import EditMenuObserver


class TextEditor(Tk, CursorObserver, TextObserver):

  _model: TextEditorModel = None
  _clipboard: ClipboardStack = None
  _list_of_text_ids: List[int] = []
  _copyAction: Action = None
  MARGIN: int = 5
  LINE_INDENT: int = 20
      
  
  class PasteAction(Action, ClipboardObserver):
    _observers: List[ActionObserver] = []

    def __init__(self, model: TextEditorModel, clipboard: ClipboardStack) -> None:
      super().__init__(model, clipboard)

    def attachActionObserver(self, observer):
      self._observers.append(observer)

    def actionPerformed(self) -> None:
      self._model.insert(self._clipboard.get_text())
    
    def updateClipboard(self):
      for observer in self._observers:
        observer.updateActionObserver(self._clipboard.isEmpty())

  
  class CopyAction(Action, CursorObserver):
    _observers: List[ActionObserver] = []

    def __init__(self, model: TextEditorModel, clipboard: ClipboardStack) -> None:
      super().__init__(model, clipboard)

    def attachActionObserver(self, observer):
      self._observers.append(observer)
    
    def actionPerformed(self) -> None:
      self._clipboard.push(self._model.getSelectionText())

    def updateCursorLocation(self) -> None:
      print(bool(self._model.selectionRange))
      for observer in self._observers:
        observer.updateActionObserver(not bool(self._model.selectionRange))
    

  class CutAction(Action, CursorObserver):
    _observers: List[ActionObserver] = []

    def __init__(self, model: TextEditorModel, clipboard: ClipboardStack) -> None:
      super().__init__(model, clipboard)

    def attachActionObserver(self, observer):
      self._observers.append(observer)
    
    def actionPerformed(self) -> None:
      self._clipboard.push(self._model.getSelectionText())
      self._model.deleteRange()

    def updateCursorLocation(self) -> None:
      for observer in self._observers:
        observer.updateActionObserver(not bool(self._model.selectionRange))

  
  class PasteAndRemoveAction(Action, ClipboardObserver):
    _observers: List[ActionObserver] = []
    
    def __init__(self, model: TextEditorModel, clipboard: ClipboardStack) -> None:
      super().__init__(model, clipboard)

    def attachActionObserver(self, observer):
      self._observers.append(observer)
    
    def actionPerformed(self) -> None:
      self._model.insert(self._clipboard.pop_get_text())
    
    def updateClipboard(self):
      for observer in self._observers:
        observer.updateActionObserver(self._clipboard.isEmpty())
  

  class DeleteSelectionAction(Action, CursorObserver):
    _observers: List[ActionObserver] = []

    def __init__(self, model: TextEditorModel, clipboard: ClipboardStack) -> None:
      super().__init__(model, clipboard)

    def attachActionObserver(self, observer):
      self._observers.append(observer)

    def actionPerformed(self) -> None:
      self._model.deleteRange()
  
    def updateCursorLocation(self) -> None:
      for observer in self._observers:
        observer.updateActionObserver(not bool(self._model.selectionRange))
  

  class UndoAction(Action, UndoManagerObserver):
    _observers: List[ActionObserver] = []
    _undoManager = UndoManager()

    def __init__(self, model: TextEditorModel, clipboard: ClipboardStack) -> None:
      super().__init__(model, clipboard)

    def attachActionObserver(self, observer):
      self._observers.append(observer)

    def actionPerformed(self) -> None:
      self._undoManager.undo()

    def updateActionStack(self):
      for observer in self._observers:
        observer.updateActionObserver(self._undoManager._undoStack.isEmpty())

  class RedoAction(Action, UndoManagerObserver):
    _observers: List[ActionObserver] = []
    _undoManager = UndoManager()

    def __init__(self, model: TextEditorModel, clipboard: ClipboardStack) -> None:
      super().__init__(model, clipboard)

    def attachActionObserver(self, observer):
      self._observers.append(observer)

    def actionPerformed(self) -> None:
      self._undoManager.redo()

    def updateActionStack(self):
      for observer in self._observers:
        observer.updateActionObserver(self._undoManager._redoStack.isEmpty())

  def __init__(self, model: TextEditorModel) -> None:
    super().__init__()
    self._model = model
    self._clipboard = ClipboardStack()
    self._pasteAction = self.PasteAction(self._model, self._clipboard)
    self._cutAction = self.CutAction(self._model, self._clipboard)
    self._copyAction = self.CopyAction(self._model, self._clipboard)
    self._pasteAndRemoveAction = self.PasteAndRemoveAction(self._model, self._clipboard)
    self._deleteSelectionAction = self.DeleteSelectionAction(self._model, self._clipboard)
    self._undoAction = self.UndoAction(self._model, self._clipboard)
    self._redoAction = self.RedoAction(self._model, self._clipboard)
    self._clipboard.attachClipboardObserver(self._pasteAction)
    self._clipboard.attachClipboardObserver(self._pasteAndRemoveAction)

    self._undoManager = UndoManager()
    self._undoManager.attach(self._undoAction)
    self._undoManager.attach(self._redoAction)

    self._model.attachCursorObserver(self)
    self._model.attachTextObserver(self)
    self._model.attachCursorObserver(self._copyAction)
    self._model.attachCursorObserver(self._cutAction)
    self._model.attachCursorObserver(self._deleteSelectionAction)

    self.initGUI()


  def initGUI(self):
    self.title('Text Editor')
    self.geometry("600x300")

    self._canvas = Canvas(self, bg='white')
    self._canvas.pack(side=BOTTOM, fill=BOTH, expand=1)

    self.initToolbar()  
    self.initMenubar()

    self.drawLines()
    self.drawCursor()

    self.bind('<KeyPress>', self.onKeyPress)
  
  def initMenubar(self):
    self._menu = Menu(self)
    self.config(menu=self._menu)

    file_menu = Menu(self._menu)
    self._menu.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Open")
    file_menu.add_command(label="Save")
    file_menu.add_command(label="Exit", command=self.quit)

    edit_menu = Menu(self._menu)
    self._menu.add_cascade(label="Edit", menu=edit_menu)
    edit_menu.add_command(label="Undo", command=self._undoManager.undo, state="disabled")
    self._undoAction.attachActionObserver(EditMenuObserver(edit_menu, "Undo"))
    edit_menu.add_command(label="Redo", command=self._undoManager.redo)
    self._redoAction.attachActionObserver(EditMenuObserver(edit_menu, "Redo"))
    edit_menu.add_command(label="Cut", command=self._cutAction.actionPerformed, state="disabled")
    self._cutAction.attachActionObserver(EditMenuObserver(edit_menu, "Cut"))
    edit_menu.add_command(label="Copy", command=self._copyAction.actionPerformed, state="disabled")
    self._copyAction.attachActionObserver(EditMenuObserver(edit_menu, "Copy"))
    edit_menu.add_command(label="Paste", command=self._pasteAction.actionPerformed, state="disabled")
    self._pasteAction.attachActionObserver(EditMenuObserver(edit_menu, "Paste"))
    edit_menu.add_command(label="Paste and Take", command=self._pasteAndRemoveAction.actionPerformed, state="disabled")
    self._pasteAndRemoveAction.attachActionObserver(EditMenuObserver(edit_menu, "Paste and Take"))
    edit_menu.add_command(label="Delete selection", command=self._deleteSelectionAction.actionPerformed, state="disabled")
    self._deleteSelectionAction.attachActionObserver(EditMenuObserver(edit_menu, "Delete selection"))
    edit_menu.add_command(label="Clear document")
  
    move_menu = Menu(self._menu)
    self._menu.add_cascade(label="Move", menu=move_menu)
    move_menu.add_command(label="Cursor to document start", command=self._model.moveCursorToDocumentStart)
    move_menu.add_command(label="Cursor to document end", command=self._model.moveCursorToDocumentEnd)

    plugin_menu = Menu(self._menu)
    self._menu.add_cascade(label="Plugin", menu=plugin_menu)
  
  def initToolbar(self):
    self._button_canvas = Canvas(self)

    b1 = Button(self._button_canvas, text="Undo", command=self._undoManager.undo, state="disabled")
    b1.pack(side=LEFT)
    self._undoAction.attachActionObserver(ButtonObserver(b1))
    b2 = Button(self._button_canvas, text="Redo", command=self._undoManager.redo, state="disabled")
    b2.pack(side=LEFT)
    self._redoAction.attachActionObserver(ButtonObserver(b2))
    b3 = Button(self._button_canvas, text="Cut", command=self._cutAction.actionPerformed, state="disabled")
    b3.pack(side=LEFT)
    self._cutAction.attachActionObserver(ButtonObserver(b3))
    b4 = Button(self._button_canvas, text="Copy", command=self._copyAction.actionPerformed, state="disabled")
    b4.pack(side=LEFT)
    self._copyAction.attachActionObserver(ButtonObserver(b4))
    b5 = Button(self._button_canvas, text="Paste", command=self._pasteAction.actionPerformed, state="disabled")
    b5.pack(side=LEFT)
    self._pasteAction.attachActionObserver(ButtonObserver(b5))
    self._button_canvas.pack(side=TOP, fill=BOTH, expand=2)

  def onKeyPress(self, event):
    if event.keysym == 'Left':
      if event.state == 262153:
        self._model.addSelectionOnLeft()
      else:
        self._model.clearSelection()
        self._model.moveCursorLeft()
    elif event.keysym == 'Right':
      if event.state == 262153:
        self._model.addSelectionOnRight()
      else:
        self._model.clearSelection()
        self._model.moveCursorRight()
    elif event.keysym == 'Down':
      self._model.moveCursorDown()
    elif event.keysym == 'Up':
      self._model.moveCursorUp()
    elif event.keysym == 'Delete':
      if self._model.selectionRange:
        self._model.deleteRange()
      else:  
        self._model.deleteAfter()
    elif event.keysym == 'BackSpace':
      if self._model.selectionRange:
        self._model.deleteRange()
      else:
        self._model.deleteBefore()
    elif event.keysym.isalpha() or event.keysym.isnumeric():
      if event.char == '\x03':
        self._copyAction.actionPerformed()
      elif event.char == '\x16':
        if event.state == 13:
          self._pasteAndRemoveAction.actionPerformed()
        else:
          self._pasteAction.actionPerformed()
      elif event.char == '\x18':
        self._cutAction.actionPerformed()
      elif event.char == '\x1a':
        self._undoManager.undo()
      elif event.char == '\x19':
        self._undoManager.redo()
      else:
        self._model.insert(event.keysym)

  def drawLines(self):
    all_lines = self._model.allLines()
    i=0
    while True:
      try:
        text = next(all_lines)
        self._text_id = self._canvas.create_text(self.MARGIN, i*self.LINE_INDENT, text=text, anchor="nw")
        self._list_of_text_ids.append(self._text_id)
        i += 1
      except StopIteration:
        break
  
  def drawSelection(self):
    if self._model.selectionRange:     
      cursorLocation = self._model.cursorLocation
      line_height = tkFont.Font(font='TkDefaultFont').metrics('linespace')

      selection_start = self._model.lines[self._model.selectionRange.start.y][0:self._model.selectionRange.start.x]
      selection_end = self._model.lines[self._model.selectionRange.end.y][0:self._model.selectionRange.end.x]
      line_width_start = tkFont.Font(font='TkDefaultFont').measure(selection_start)
      line_width_end = tkFont.Font(font='TkDefaultFont').measure(selection_end)

      y_start = self._model.selectionRange.start.y*self.LINE_INDENT
      y_end = y_start + line_height
      x_start = self.MARGIN + line_width_start
      x_end = self.MARGIN + line_width_end

      try:
        self._canvas.coords(self._rect_id, x_start, y_start, x_end, y_end)
      except Exception:
        self._rect_id = self._canvas.create_rectangle(
          x_start, y_start,
          x_end, y_end,
          fill='#0099ff',
          outline='white'
        )
        self._canvas.tag_raise(self._list_of_text_ids[cursorLocation.y], self._rect_id)
    else:
      try:
        self._canvas.delete(self._rect_id)
        self._rect_id = None
      except:
        pass

  def updateCursorLocation(self) -> None:
    self.drawCursor()

  def updateText(self):
    for text_id in self._list_of_text_ids:
      self._canvas.delete(text_id)
    self._list_of_text_ids = []
    self.drawLines()
    self.drawSelection()
  
  def drawCursor(self) -> None:
    cursorLocation = self._model.cursorLocation

    if self._model.lines:
      line = self._model.lines[cursorLocation.y][0:cursorLocation.x]
    else:
      line = ""
    
    line_width = tkFont.Font(font='TkDefaultFont').measure(line)
    line_height = tkFont.Font(font='TkDefaultFont').metrics('linespace')

    x1_cursor = self.MARGIN + line_width
    y1_cursor = cursorLocation.y*self.LINE_INDENT
    x2_curosr = x1_cursor
    y2_cursor = y1_cursor + line_height
    
    try:
      self._canvas.coords(self._cursor_id, x1_cursor, y1_cursor, x2_curosr, y2_cursor)
    except:
      self._cursor_id = self._canvas.create_line(x1_cursor, y1_cursor, x2_curosr, y2_cursor)

  @property
  def model(self) -> TextEditorModel:
    return self._model