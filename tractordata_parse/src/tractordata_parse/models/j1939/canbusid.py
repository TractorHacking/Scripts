from tractordata_parse.models.j1939 import CanbusPGN

class CanbusIDView:
  def __init__(self, id):
    self.base_id = 0
    if type(id) is str:
      # not the actual id but whatever for some reason we've got a null ID
      if id == '':
        id = "0"
      self.base_id = int(id, 16)
    elif type(id) is int:
      self.base_id = id
    
  def __str__(self):
    return ("0x%08x" % self.base_id)
    
  # As per the "Data link layer" document
  @property
  def pgn(self):
    _pgn = (self.pf << 8)
    if self.isGroupExt(): # PF >= 240; PF >= 0xF0
      _pgn |= self.ps
    return _pgn
    
  @property
  def pf(self):
    return (self.base_id & 0x00FF0000) >> 16
    
  @property
  def ps(self):
    return (self.base_id & 0x0000FF00) >> 8
  
  @property
  def dest(self):
    return -1 if self.isGroupExt else self.ps
  
  @property
  def source(self):
    return (self.base_id & 0x000000FF) # >> 0
    
  @property
  def dataPage(self):
    return (self.base_id & 0x03000000) >> 24
    
  @property
  def priority(self):
    return (self.base_id & 0x1C000000) >> 26
    
  # state queries
  @property
  def isGroupExt(self):
    return (self.pf >= 240)
    
  #Combo modes
  # We fiddle with the byte ordering to make sorting more useful
  def getPGNAndDataPage(self):
    return (self.pgn << 4) | (self.dataPage)
    
  def getPGNAndPriority(self):
    return (self.pgn << 4) | (self.priority)
    
  def getPGNAndSource(self):
    return (self.pgn << 8) | (self.source)
    
  def getSourceAndPGN(self):
    return (self.source << 16) | (self.pgn)
    
  def toString(self, args):
    strlist = [str(self)]
    if args.show_pgn:
      strlist.append("PGN: " + CanbusPGN(self.pgn).toString(args))
    if args.show_src:
      strlist.append("Source: " + "{:#04x}".format(self.source))
    if args.show_dest:
      strlist.append("Destination: " + "{:#04x}".format(self.dest))
    if args.show_pri:
      strlist.append("Priority: " + str(self.priority))
    if args.show_dp:
      strlist.append("Data Page: " + str(self.datapage))
    return "["+(", ".join(strlist))+"]"
