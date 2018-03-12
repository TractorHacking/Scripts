class CanbusPGN:
  def __init__(self, id):
    self.base_pgn = 0
    if type(id) is str:
      self.base_pgn = int(id, 16)
    elif type(id) is int:
      self.base_pgn = id
    
  def __str__(self):
    return "{:#06x}, {}".format(self.base_pgn, self.base_pgn)
    
  def toString(self, args):
    strlist = [str(self)]
    return "("+(", ".join(strlist))+")"
