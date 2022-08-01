from .action_observer import ActionObserver


class EditMenuObserver(ActionObserver):

  def __init__(self, em, name) -> None:
    self._em = em
    self._name = name
  
  def updateActionObserver(self, flag):
    if flag:
      self._em.entryconfig(self._name, state="disabled")
    else:
      self._em.entryconfig(self._name, state="normal")