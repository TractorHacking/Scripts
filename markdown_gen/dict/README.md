The program make_dict.py looks through the list of all the registered PGNs in the SAE J1939 directory and 
creates a dictionary that holds all the relevant information about them. The program reads each entry into
an object type named pgn, that is specified in the file pgn.py. Each individual pgn has a list of attributes
that are sent under that pgn, and details on their byte size and offset, and description. The resulting dictionary
is serialized using the Pickle library and saved into a file named pgndict. This file can be deserialized 
using the Pickle library, found here: [Pickle](https://docs.python.org/2/library/pickle.html).
```
Usage: python make_dict.py
```
No arguments are needed.
make_dict.py requires that the list of SAE PGNs are stored in a file in the current directory, named PGN.csv. 
This must use standard comma delimination. The outut dictionary is stored in a file pgndict, also in the current
directory. If this file does not exist, it will be created for you, and if it does exist, all contents will be 
overwritten.
