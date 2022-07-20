from plugin import Plugin


class StatisticsPlugin(Plugin):

  def getName() -> str:
    return "Statistics"

  def getDescription() -> str:
    return "Counts rows, words and letters in document"
  
  def execute(model, undoManager, clipboardStack) -> None:
    lines = model.lines
    numOfLines = 0
    numOfWords = 0
    numOfLetters = 0
    for line in lines:
      tmp = line.split(" ")
      for i in range(0, len(tmp), 1):
        numOfLetters += len(tmp[i])
        numOfWords += 1
      numOfLines += 1
