# Tractordata_parse
A program to extract J1939 data from .csv files, and output it in a useful format.

# Usage

tractordata_parse \(collate|id-info|dump-ids\) \[(FILE|DIR) ...\] \[FLAGS]

Accepts paths to compatible .csv files (generated from the agilent scope) as arguments.
If no paths are given, the program defaults to scanning the "data" directory in the current working directory.
Directories given will be recursively scanned for .csv files.
Non-directory files given will be read directly.

Currently 3 modes of operation:
  collate
    Lists all packets from the given files
    
  id-info
    Lists information specific to a given CAN ID within all the given files
    NOTE: this option requires a unique flag, `--target-id ID`, where `ID` is a
    hexadecimal value corresponding to one of the keys used by the current sort mode.
    You can get these keys by using the `dump-ids` mode, with the `--show-keys` flag.
    The `--target-id ID` flag may be repeated multiple times to dump information on multiple
    packets.
    
  dump-ids
    Outputs a list of every unique ID from within all the given files.
    
Exactly one of these commands is required per each successful invocation.

## Sort modes:
All of these are mutually exclusive.
### Primary Sorts
  --sortby-id
    (Default) Sorts by the full CAN ID of each packet.
  --sortby-pgn
    Sorts by the `PGN` field of each packet.
  --sortby-src
    Sorts by the `source` field of each packet.
  --sortby-pri
    Sorts by the `priority` field of each packet.
  --sortby-dest
    Sorts by the `destination` field of each packet. Do note that certain J1939 PGNs do not have a destination field.
### Bundled Sorts
  --sortby-pgndp
    Sorts by the `PGN` concatenated with the `data page` field of each packet.
  --sortby-pgnpri
    Sorts by the `PGN` concatenated with the `priority` field of each packet.
  --sortby-pgnsrc
    Sorts by the `PGN` concatenated with the `source` field of each packet.
  --sortby-srcpgn
    Sorts by the `source` concatenated with the `PGN` field of each packet. (This is for ordering purposes)
    
## Show modes:
  --show-src
    Shows the `src` field of each CAN ID.
  --show-pri
    Shows the `priority` field of each CAN ID.
  --show-dp
    Shows the `data page` field of each CAN ID.
  --show-pgn
    Shows the `PGN` field of each CAN ID.
  --show-dest
    Shows the `destination` field of each CAN ID. Do note that packets with `PGN` values of `0xF000` or greater do not have `destination` values.
    
## Misc options:
  --verbose
    Makes the program more chatty about minor details.

## Mode-specific options:
### id-info
  --target-id ID
    `ID` must be a key that matches the current sort mode - you can get appropriate keys by using the `--show-keys` flag with the `dump-ids` mode.

### dump-ids
  --show-keys
    Shows the keys used by the selected sort mode in the final output. Not always needed, but guarantees something usable.
  --diff-friendly
    Removes line numbers and packet counts to make it easier to compare sets of packets found within given files.
