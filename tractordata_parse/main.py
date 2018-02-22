#! /usr/bin/env python3

import csv
from pprint import pprint

from enum import Enum, auto
import argparse
import os
import sys
import itertools

# this function is probably wholly unnecessary and non-idiomatic
def squashKeys(d, hashfn):
  newdict = dict()
  # this is a list of lists of IDs that share the same PGN
  #iterthing = itertools.groupby(ids_dict.keys(), lambda canid: CanBusID(canid).getPGN())
  iterthing = itertools.groupby(d.keys(), hashfn)
  # we need to use this to create a dictionary that uses these PGNs as keys
  # the existing dictionary contains lists of dictionaries that each correspond to a
  # packet
  # we want to concatenate all such lists that match those packets to a single list
  # and then use those to create a new dictionary to iterate through
  # I think I'm overlooking a more idiomatic way of doing this
  # using "sum" maybe?
  for pgn, matching_ids in iterthing:
    # matching_ids is a list of IDs that share the same PGN value
    for i in matching_ids:
      packetlist = newdict.setdefault(pgn, [])
      packetlist.extend(d[i])
  return newdict

class SortMode(Enum):
  by_id  = auto()
  by_pgn = auto()
  by_src = auto()
  by_pri = auto()
  by_pgndp = auto()
  by_pgnpri = auto()
  by_pgnsrc = auto()


# I've gone off the deep end
sortmode_traits = {
  SortMode.by_id: {
    "length": 8,
    "idtype_str": "ID",
    "dict_transform": lambda d: d,
    "idtype_transform": lambda s, args: CanbusID(s).toString(args)
  },
  SortMode.by_pgn: {
    "length": 4,
    "idtype_str": "PGN",
    "dict_transform": lambda d: squashKeys(d, lambda id_no: "{:#06x}".format(CanbusID(id_no).getPGN())),
    "idtype_transform": lambda s, args: str(CanbusPGN(s))
  },
  SortMode.by_src: {
    "length": 2,
    "idtype_str": "Source",
    "dict_transform": lambda d: squashKeys(d, lambda id_no: "{:#04x}".format(CanbusID(id_no).getSource())),
    "idtype_transform": lambda s, args: s
  },
  SortMode.by_pri: {
    "length": 1,
    "idtype_str": "Priority",
    "dict_transform": lambda d: squashKeys(d, lambda id_no: "{:#03x}".format(CanbusID(id_no).getPriority())),
    "idtype_transform": lambda s, args: s
  },
  SortMode.by_pgndp: {
    "length": 5,
    "idtype_str": "PGN+Data Page",
    "dict_transform": lambda d: squashKeys(d, lambda id_no: "{:#07x}".format(CanbusID(id_no).getPGNAndDataPage())),
    "idtype_transform": lambda s, args: "{}, Data Page {}".format(CanbusPGN((int(s,16) & 0xFFFF0) >> 4), (int(s,16) & 0x0000F)) if not args.show_keys else s
  },
  SortMode.by_pgnpri: {
    "length": 5,
    "idtype_str": "PGN+Priority",
    "dict_transform": lambda d: squashKeys(d, lambda id_no: "{:#07x}".format(CanbusID(id_no).getPGNAndPriority())),
    "idtype_transform": lambda s, args: "{}, Priority {}".format(CanbusPGN((int(s,16) & 0xFFFF0) >> 4), (int(s,16) & 0x0000F)) if not args.show_keys else s
  },
  SortMode.by_pgnsrc: {
    "length": 6,
    "idtype_str": "PGN+Source",
    "dict_transform": lambda d: squashKeys(d, lambda id_no: "{:#08x}".format(CanbusID(id_no).getPGNAndSource())),
    "idtype_transform": lambda s, args: "{}, Source {:#04x}".format(CanbusPGN((int(s,16) & 0xFFFF00) >> 8), (int(s,16) & 0x0000FF)) if not args.show_keys else s
  }
}

class CanbusID:

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
    
  def getPGN(self):
    return (self.base_id & 0x00FFFF00) >> 8
  
  def getSource(self):
    return (self.base_id & 0x000000FF) # >> 0
    
  def getDataPage(self):
    return (self.base_id & 0x03000000) >> 24
    
  def getPriority(self):
    return (self.base_id & 0x1C000000) >> 26
    
    
  #Combo modes
  # We fiddle with the byte ordering to make sorting more useful
  def getPGNAndDataPage(self):
    return (self.getPGN() << 4) | (self.getDataPage())
    
  def getPGNAndPriority(self):
    return (self.getPGN() << 4) | (self.getPriority())
    
  def getPGNAndSource(self):
    return (self.getPGN() << 8) | (self.getSource())
    
  def toString(self, args):
    strlist = [str(self)]
    if args.show_pgn:
      strlist.append("PGN: " + str(CanbusPGN(self.getPGN())))
    if args.show_src:
      strlist.append("Source: " + str(self.getSource()))
    if args.show_pri:
      strlist.append("Priority: " + str(self.getPriority()))
    if args.show_dp:
      strlist.append("Data Page: " + str(self.getDataPage()))
    return "["+(", ".join(strlist))+"]"

class CanbusPGN:
  def __init__(self, id):
    self.base_pgn = 0
    if type(id) is str:
      self.base_pgn = int(id, 16)
    elif type(id) is int:
      self.base_pgn = id
    
  def __str__(self):
    return "({:#06x}, {})".format(self.base_pgn, self.base_pgn)

class CanbusData:
  def __init__(self):
  
    self.ids_dict = {}
    self.packet_sequence = []
    self.error_count = 0
    self.files_scanned = []
  
  def read(self, fpath, verbose=False):
    if verbose:
      print( "reading: " + fpath, file=sys.stderr)
    self.files_scanned.append(fpath)
    with open(fpath) as infile:
      reader = csv.reader(infile)
      # Skip first "header" row

      header_row = next(reader)

      err_index = header_row.index("Errors")
      ID_index = header_row.index("ID")
      data_index = header_row.index("Data")
      time_index = header_row.index("Time")
      
      # 9 columns per row
      for row in reader:
        # row has an error
        if len(row[err_index]) != 0:
          self.error_count = self.error_count + 1
          continue
        # data is null
        if len(row[data_index]) == 0:
          continue
        # goofy trick to make the ID uniform
        can_id = "{0:#010x}".format(int(row[ID_index] if row[ID_index] is not '' else '0', 16))
        id_data = self.ids_dict.setdefault(can_id, [])
        pinfo_dict = { "data": row[data_index], "time": row[time_index], "ID": can_id, "sourceFile": fpath }
        id_data.append(pinfo_dict)
        self.packet_sequence.append(pinfo_dict)

  def printDataByID(self, args):
    print("====SECTION Data by ID====")
    identifier_map = sortmode_traits[args.sortmode]["dict_transform"](self.ids_dict)
    
    for thing in sorted(identifier_map.keys()):
      idstr = sortmode_traits[args.sortmode]["idtype_transform"](thing, args)
      print("%s: (%d entries)" % (idstr, len(identifier_map[thing])))
      for data in identifier_map[thing]:
        if len(self.files_scanned) > 1:
          print("\t({:>50})".format(data["sourceFile"]), end='')
        if args.sortmode is not SortMode.by_id:
          print("\t{}".format(data["ID"]), end='')
        print("\t{}".format(data["time"]))
        print("\t\t{}".format(data["data"]))
        
  def printAllIDs(self, args):
    identifier_map = sortmode_traits[args.sortmode]["dict_transform"](self.ids_dict)
      
    l = sorted(identifier_map.keys())
    for i in range(len(l)):
      idstr = sortmode_traits[args.sortmode]["idtype_transform"](l[i], args)
      
      print("%2d" % i, idstr, "(%d entries across all checked files)" % len(identifier_map[l[i]]))
        
  def printDataOnCanID(self, idstring, args):
    files_set = set()
    
    identifier_map = sortmode_traits[args.sortmode]["dict_transform"](self.ids_dict)
    
    idstr_print = idstring
    # format the full id according to args
    if args.sortmode is SortMode.by_id:
      idstr_print = CanbusID(idstring).toString(args)
      

    if not (idstring in identifier_map.keys()):
      print("Key '%s' not present in %d scanned file(s)" % (idstring, len(self.files_scanned)))
      return
    
    packets_list = identifier_map[idstring]
    print("====SECTION Data of %s '%s'====" % (sortmode_traits[args.sortmode]["idtype_str"], idstr_print))
    
    print("(%d entries across all %d scanned file(s))" % (len(packets_list), len(self.files_scanned)))
    # We want an iterable for which 
    for data in packets_list:
      print("\t{}".format(data["time"]), end='')
      if args.sortmode is not SortMode.by_id:
        print("\t{}".format(CanbusID(data["ID"]).toString(args)), end='')
      if len(self.files_scanned) > 1:
        print("\t({:>50})".format(data["sourceFile"]), end='')
      print() # newline
      print("\t\t{}".format(data["data"]))
      files_set.add(data["sourceFile"])
    print("Found in the following files:")
    pprint(files_set)

  
# the actual driving magic is here
if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Get unique CAN-Bus IDs.')
  
  # we do a common parser instead of adding them all above because otherwise
  # argparse goes bonkers and you have to stick all the flags in front of the action
  # which is weird
  common_parser = argparse.ArgumentParser(add_help=False)
  common_parser.add_argument('data_path', nargs="*", type=str, help="Paths to csv files containing data, or a directory to scan for such files. If absent, scans the \"data\" directory.")
  
  common_parser.add_argument('--show-src', action='store_true', help="Shows the source address for each CAN ID")
  common_parser.add_argument('--show-pri', action='store_true', help="Shows the priority of each CAN ID")
  common_parser.add_argument('--show-dp', action='store_true', help="Shows the data page of each CAN ID")
  common_parser.add_argument('--show-pgn', action='store_true', help="Shows the decimal PGN key for each CAN ID")
  common_parser.add_argument('--verbose', action='store_true', help="Makes the program more chatty about minor details")
  common_parser.set_defaults(show_keys=False)
  
  sortmodes_gp = common_parser.add_mutually_exclusive_group()
  sortmodes_gp.set_defaults(sortmode=SortMode.by_id)
  sortmodes_gp.add_argument('--sortby-pgn',    dest='sortmode', action='store_const', const=SortMode.by_pgn,    help="Groups by PGN instead of the full ID")
  sortmodes_gp.add_argument('--sortby-id',     dest='sortmode', action='store_const', const=SortMode.by_id ,    help="Groups by full ID")
  sortmodes_gp.add_argument('--sortby-src',    dest='sortmode', action='store_const', const=SortMode.by_src,    help="Groups by source device")
  sortmodes_gp.add_argument('--sortby-pri',    dest='sortmode', action='store_const', const=SortMode.by_pri,    help="Groups by priority")
  sortmodes_gp.add_argument('--sortby-pgndp',  dest='sortmode', action='store_const', const=SortMode.by_pgndp,  help="Groups by PGN+Data page")
  sortmodes_gp.add_argument('--sortby-pgnpri', dest='sortmode', action='store_const', const=SortMode.by_pgnpri, help="Groups by PGN+Priority")
  sortmodes_gp.add_argument('--sortby-pgnsrc', dest='sortmode', action='store_const', const=SortMode.by_pgnsrc, help="Groups by PGN+Source")
  
  subparsers = parser.add_subparsers(dest="action_type")
  subparsers.required = True

  def collate(args):
    cbdata.printDataByID(args)
  
  def id_info(args):
    for tidlist in args.target_id:
      tid = tidlist[0] # the lists have only 1 entry
      temp_tid = None
      try:
        temp_tid = int(tid)
      except ValueError:
        try:
          temp_tid = int(tid, 16)
        except ValueError:
          print("Unable to parse ID {}".format(tid))
          sys.exit(1)
      tid = "{0:#0{1}x}".format(temp_tid, 2 + sortmode_traits[args.sortmode]["length"])
      cbdata.printDataOnCanID(tid, args)
      
  def dump_ids(args):
    cbdata.printAllIDs(args)

  collate_action = subparsers.add_parser('collate', parents=[common_parser], help='List the signals from each file')
  collate_action.set_defaults(func=collate)
  
  info_action = subparsers.add_parser('id-info', parents=[common_parser], help='Print info specific to a single CAN ID. Requires at least one target ID flag')
  info_action.add_argument('--target-id', action='append', nargs=1, help="A specific ID to show more info on. Required by the 'id_info' mode", required=True)
  info_action.set_defaults(func=id_info)
  
  dump_action = subparsers.add_parser('dump-ids', parents=[common_parser], help='Dump all unique CAN IDs from the files')
  dump_action.add_argument('--show-keys', action='store_true', help="Show the keys for use in the 'target-id' statement")
  dump_action.set_defaults(func=dump_ids)
  
  args = parser.parse_args()
  
  cbdata = CanbusData()
  
  # No path specified, scan the "data" folder for sheets
  if len(args.data_path) == 0:
    args.data_path = ["data"]
    
  target_list = []
  for p in args.data_path:
    if os.path.isdir(p):
      visited_set = set()
      for root, dirs, files in os.walk(p, topdown=True, followlinks=True):
        visited_set.add(os.path.realpath(root))
        for d in dirs.copy():
          true_path = os.path.realpath(os.path.join(root, d))
          # prune walking directories already visited
          # necessary to avoid infinite recursion with followlinks
          if true_path in visited_set:
            dirs.remove(d)
        for f in files:
          if not f.endswith(".csv"):
            continue
          target_list.append(os.path.join(root, f))
    else:
      target_list.append(p)

  for t in target_list:
    try:
      cbdata.read(t, args.verbose)
    except UnicodeDecodeError as e:
      print("Error when reading file %s: %s" % (t, e), file=sys.stderr)
      
  args.func(args)
