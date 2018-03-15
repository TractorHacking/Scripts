import cPickle
import pgn

PGN = 4
DESCRIPTION = 5
BYTEOFFSET = 17
ATTR_DESC = 19
SIZE = 21

def main():
	pgnfile = open('PGN.csv', 'r')
	dictfile = open('pgndict.txt', 'wb')

	dict = {}

	line = pgnfile.readline()
	for line in pgnfile:
		vals = line.split(',')
		if(not line_valid(vals)): #if the current line does not have all the needed info, skip it
			if(len(vals[DESCRIPTION].split()) > 0 and vals[DESCRIPTION].split()[0] == 'Proprietary'):
				dict[vals[PGN]] = pgn.pgn(vals[PGN], vals[DESCRIPTION], None)
			continue
		if vals[PGN] not in dict:
			dict[vals[PGN]] = pgn.pgn(vals[PGN], vals[DESCRIPTION], [])
		dict[vals[PGN]].attributes.append(pgn.attribute(vals[ATTR_DESC], vals[BYTEOFFSET], vals[SIZE]))

	cPickle.dump(dict, dictfile)

def line_valid(vals):
	try:
		if(len(vals[PGN]) == 0 or 
			len(vals[DESCRIPTION]) == 0 or
			len(vals[ATTR_DESC]) == 0 or
			len(vals[BYTEOFFSET]) == 0 or
			len(vals[SIZE]) == 0):
			return False
	except KeyError:
		return False
	return True

if __name__=="__main__":
	main()
