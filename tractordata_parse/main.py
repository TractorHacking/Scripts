#! /usr/bin/env python3

import csv
from pprint import pprint
import argparse
import os

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
    
  def toString(self, *args, showPGN=False, showSource=False, showPriority=False, showDataPage=False):
    strlist = [str(self)]
    if showPGN:
      strlist.append("PGN: " + str(self.getPGN()))
    if showSource:
      strlist.append("Source: " + str(self.getSource()))
    if showPriority:
      strlist.append("Priority: " + str(self.getPriority()))
    if showDataPage:
      strlist.append("Data Page: " + str(self.getDataPage()))
    return "["+(", ".join(strlist))+"]"

class CanbusData:

  def __init__(self, *args, showPGN=False, showSource=False, showPriority=False, showDataPage=False):
  
    self.ids_dict = {}
    self.packet_sequence = []
    self.error_count = 0
    self.files_scanned = []
    self.showPGN = showPGN
    self.showSource = showSource
    self.showPriority = showPriority
    self.showDataPage = showDataPage
  
  def read(self, fpath):
    self.files_scanned.append(fpath)
    infile = open(fpath)
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
      id_data = self.ids_dict.setdefault(row[ID_index], [])
      pinfo_dict = { "data": row[data_index], "time": row[time_index], "ID": row[ID_index], "sourceFile": fpath }
      id_data.append(pinfo_dict)
      self.packet_sequence.append(pinfo_dict)

  def printDataByID(self):
    print("====SECTION Data by ID====")
    for thing in sorted(self.ids_dict.keys()):
      cbid = CanbusID(thing)
      idstr = cbid.toString(showPGN=self.showPGN, showSource=self.showSource, showPriority=self.showPriority, showDataPage=self.showDataPage)
      print("%s: (%d entries)" % (idstr, len(self.ids_dict[thing])))
      for data in self.ids_dict[thing]:
        if len(self.files_scanned) <= 1:
          print("\t%s\n\t\t%s" % (data["time"], data["data"]))
        else:
          print("\t%-50s\t%s\n\t\t%s" % ("(%s)" % data["sourceFile"], data["time"], data["data"]))
        
  def printAllIDs(self):
    l = sorted(self.ids_dict.keys())
    for i in range(len(l)):
      cbid = CanbusID(l[i])
      idstr = cbid.toString(showPGN=self.showPGN, showSource=self.showSource, showPriority=self.showPriority, showDataPage=self.showDataPage)
      print("%2d" % i, idstr, "(%d entries across all checked files)" % len(self.ids_dict[l[i]]))
        
  def printDataOnCanID(self, idstring):
    cbid = CanbusID(idstring)
    print("====SECTION Data of ID '%s'====" % idstring)
    # help i should not be allowed within 50 feet of kwargs
    print(cbid.toString(showPGN=self.showPGN, showSource=self.showSource, showPriority=self.showPriority, showDataPage=self.showDataPage))
    print("(%d entries across all %d scanned file(s))" % (len(self.ids_dict[idstring]), len(self.files_scanned)))
    files_set = set()
    for data in self.ids_dict[idstring]:
      print("\t%-50s\t%s\n\t\t%s" % ("(%s)" % data["sourceFile"], data["time"], data["data"]))
      files_set.add(data["sourceFile"])
    print("Found in the following files:")
    pprint(files_set)
  

#print("====SECTION Data in order====")
#print("ID keys:")
#id_reverse_map = {}
#for i in range(len(id_list)):
#  print("%2d" % i, id_list[i])
#  id_reverse_map[id_list[i]] = i


#for thing in packet_sequence:
#  print("%08s:\t[%2s]\t%s" % (thing["time"], id_reverse_map[thing["ID"]], thing["data"]))
  
# the actual driving magic is here
if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Get unique CAN-Bus IDs.')

  action = parser.add_mutually_exclusive_group(required=True)
  action.add_argument('--collate', action='store_true')
  action.add_argument('--target-id', type=str)
  action.add_argument('--dump-ids', action='store_true')

  parser.add_argument('data_path', nargs="*", type=str, help="Paths to csv files containing data. If absent, scans the \"data\" directory.")
  parser.add_argument('--show-src', action='store_true', help="Shows the source address for each CAN ID")
  parser.add_argument('--show-pri', action='store_true', help="Shows the priority of each CAN ID")
  parser.add_argument('--show-dp', action='store_true', help="Shows the data page of each CAN ID")
  parser.add_argument('--show-pgn', action='store_true', help="Shows the decimal PGN key for each CAN ID")
  args = parser.parse_args()
  
  cbdata = CanbusData(showPGN=args.show_pgn, showSource=args.show_src, showPriority=args.show_pri, showDataPage=args.show_dp)
  
  # No path specified, scan the "data" folder for sheets
  if len(args.data_path) == 0:
    for p in os.listdir("data"):
      if not p.endswith(".csv"):
        continue
      cbdata.read("data/" + p)
  else:
    for p in args.data_path:
      cbdata.read(p)
      
  if args.collate:
    cbdata.printDataByID()
  elif args.target_id:
    cbdata.printDataOnCanID(args.target_id)
  elif args.dump_ids:
    cbdata.printAllIDs()