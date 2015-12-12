class Action():
  def __init__(self, partDB):
    self.partDB = partDB

  def run(self):
    raise Exception('Action not defined')
