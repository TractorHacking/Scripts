USAGE:

Accepts paths to compatible .csv files (generated from the agilent scope) as arguments.
If no paths are given, defaults to scanning every such file within the "data" directory.
If provided files do not match the specs, the script will probably crash, sucks to be you.

Currently 3 modes of operation:
  --collate
    Lists all packets from the given files
    
  --target-id TARGET_ID
    Lists information specific to a given CAN ID within all the given files
    
  --dump-ids
    Outputs a list of every unique ID from within all the given files.
    
Exactly one of these flags is required per successful invocation.
