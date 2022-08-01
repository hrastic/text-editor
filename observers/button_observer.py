from .action_observer import ActionObserver


class ButtonObserver(ActionObserver):

  def __init__(self, button) -> None:
    self._button = button
  
  def updateActionObserver(self, flag):
    if flag:
      self._button["state"] = "disabled"
    else:
      self._button["state"] = "normal"