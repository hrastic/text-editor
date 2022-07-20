from tkinter import *
from tkinter import ttk

from text_editor.text_editor import TextEditor
from text_editor.text_editor_model import TextEditorModel


if __name__ == '__main__':
  model = TextEditorModel("Proba\nProba2\nProba")
  editor = TextEditor(model)
  editor.mainloop()
