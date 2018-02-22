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


ids_length = {
  SortMode.by_id: 8,
  SortMode.by_pgn: 4,
  SortMode.by_src: 2
}

class CanbusID:

  def __init__(self, id):
    # not the actual id but whatever for some reason we've got a null ID
    if id == '':
      id = "0"
    self.base_id = int(id, 16)
    
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
    
  def toString(self, args):
    strlist = [str(self)]
    if args.show_pgn:
      strlist.append("PGN: " + str(self.getPGN()))
    if args.show_src:
      strlist.append("Source: " + str(self.getSource()))
    if args.show_pri:
      strlist.append("Priority: " + str(self.getPriority()))
    if args.show_dp:
      strlist.append("Data Page: " + str(self.getDataPage()))
    return "["+(", ".join(strlist))+"]"

class CanbusData:
  def __init__(self, *args, ):
  
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
    identifier_map = self.ids_dict
    if args.sortmode is SortMode.by_pgn:
      identifier_map = squashKeys(self.ids_dict, lambda id_no: "{:#06x}".format(CanbusID(id_no).getPGN()))
    elif args.sortmode is SortMode.by_src:
      identifier_map = squashKeys(self.ids_dict, lambda id_no: "{:#04x}".format(CanbusID(id_no).getSource()))
      
    
    for thing in sorted(identifier_map.keys()):
      idstr = thing
      if args.sortmode is SortMode.by_id:
        idstr = CanbusID(idstr).toString(args)
      elif args.sortmode is SortMode.by_pgn:
        idstr = "{0}, {1}".format(idstr, int(idstr, 16))
      print("%s: (%d entries)" % (idstr, len(identifier_map[thing])))
      for data in identifier_map[thing]:
        if len(self.files_scanned) > 1:
          print("\t({:>50})".format(data["sourceFile"]), end='')
        if args.sortmode is not SortMode.by_id:
          print("\t{}".format(data["ID"]), end='')
        print("\t{}".format(data["time"]))
        print("\t\t{}".format(data["data"]))
        
  def printAllIDs(self, args):
    identifier_map = self.ids_dict
    
    if args.sortmode is SortMode.by_pgn:
      identifier_map = squashKeys(self.ids_dict, lambda id_no: "{:#06x}".format(CanbusID(id_no).getPGN()))
    elif args.sortmode is SortMode.by_src:
      identifier_map = squashKeys(self.ids_dict, lambda id_no: "{:#04x}".format(CanbusID(id_no).getSource()))
      
    l = sorted(identifier_map.keys())
    for i in range(len(l)):
      idstr = l[i]
      if args.sortmode is SortMode.by_id:
        idstr = CanbusID(idstr).toString(args)
      elif args.sortmode is SortMode.by_pgn:
        idstr = "{0}, {1}".format(idstr, int(idstr, 16))
      print("%2d" % i, idstr, "(%d entries across all checked files)" % len(identifier_map[l[i]]))
        
  def printDataOnCanID(self, idstring, args):
    files_set = set()
    
    # this is a dict sorted on ID
    identifier_map = self.ids_dict
    
    idtype_str = None
    
    idstr_print = idstring
    # hmm this smells vaguely of wanting a diff impl
    if args.sortmode is SortMode.by_id:
      idtype_str = "ID"
      idstr_print = CanbusID(idstring).toString(args)
    elif args.sortmode is SortMode.by_pgn:
      idtype_str = "PGN"
      identifier_map = squashKeys(self.ids_dict, lambda id_no: "{:#06x}".format(CanbusID(id_no).getPGN()))
    elif args.sortmode is SortMode.by_src:
      idtype_str = "Source"
      identifier_map = squashKeys(self.ids_dict, lambda id_no: "{:#04x}".format(CanbusID(id_no).getSource()))
      

    if not (idstring in identifier_map.keys()):
      print("Key '%s' not present in %d scanned file(s)" % (idstring, len(self.files_scanned)))
      return
    
    packets_list = identifier_map[idstring]
    print("====SECTION Data of %s '%s'====" % (idtype_str, idstr_print))
    
    print("(%d entries across all %d scanned file(s))" % (len(packets_list), len(self.files_scanned)))
    # We want an iterable for which 
    for data in packets_list:
      print("\t{}".format(data["time"]), end='')
      if args.sortmode is not SortMode.by_id:
        print("\t{}".format(data["ID"]), end='')
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
  
  sortmodes_gp = common_parser.add_mutually_exclusive_group()
  sortmodes_gp.set_defaults(sortmode=SortMode.by_id)
  sortmodes_gp.add_argument('--sortby-pgn', dest='sortmode', action='store_const', const=SortMode.by_pgn, help="Groups by PGN instead of the full ID")
  sortmodes_gp.add_argument('--sortby-id',  dest='sortmode', action='store_const', const=SortMode.by_id , help="Groups by full ID")
  sortmodes_gp.add_argument('--sortby-src', dest='sortmode', action='store_const', const=SortMode.by_src, help="Groups by source device")
  
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
      tid = "{0:#0{1}x}".format(temp_tid, 2 + ids_length[args.sortmode])
      cbdata.printDataOnCanID(tid, args)
      
  def dump_ids(args):
    cbdata.printAllIDs(args)

  collate_action = subparsers.add_parser('collate', parents=[common_parser], help='List the signals from each file')
  collate_action.set_defaults(func=collate)
  
  info_action = subparsers.add_parser('id-info', parents=[common_parser], help='Print info specific to a single CAN ID. Requires at least one target ID flag')
  info_action.add_argument('--target-id', action='append', nargs=1, help="A specific ID to show more info on. Required by the 'id_info' mode", required=True)
  info_action.set_defaults(func=id_info)
  
  dump_action = subparsers.add_parser('dump-ids', parents=[common_parser], help='Dump all unique CAN IDs from the files')
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
