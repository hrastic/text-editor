from abc import abstractmethod

from .abstract_action import AbstractAction
from text_editor.text_editor_model import TextEditorModel
from clipboard.clipboard_stack import ClipboardStack

class Action(AbstractAction):
  _enabled: str = "disabled"

  def __init__(self, model: TextEditorModel, clipboard: ClipboardStack) -> None:
    self._model = model
    self._clipboard = clipboard
  
  @property
  def enabled(self) -> str:
    return self._enabled
  
  @enabled.setter
  def enabled(self, enabled: str) -> None:
    self._enabled = enabled
    
  @abstractmethod
  def actionPerformed(self) -> None:
    pass
