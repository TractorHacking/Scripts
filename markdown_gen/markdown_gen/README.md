The program generatemd.py generates the markdown formatted pages for web documentation for the input list
of CAN ids. The list must be stored in an input file in the current directory named all_ids.txt, one id 
on each line. The program looks up each id in the previously created dictionary containing all the SAE 
specified IDs. If it finds a match, then it gathers the data from that ID stored in the dictionary. The object
structure for a CAN ID is stored in the file pgn.py. A new markdown file is generated, containing all the 
important attributes about that ID, and stored in the location of the user specified destination directory.
All the non-matched ids are stored in a file named invalid_ids.txt. If the user enters a second argument to 
the program, it will be treated as the path to a file to store the proprietary id info. It will list the CAN ID,
PGN, and proprietary name in this file, one entry per line.
```
Usage: python generatemd.py <destination> [proprietary_destination]
```
