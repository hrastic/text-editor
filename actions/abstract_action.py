from abc import ABC, abstractmethod

class AbstractAction(ABC):
  """Apstraktno sučelje koje nudi metodu za izvođenje akcije."""
  
  def actionPerformed(self) -> None:
    pass