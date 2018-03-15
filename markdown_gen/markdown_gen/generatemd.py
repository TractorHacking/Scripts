import sys
import pgn
import cPickle

def main():
	if(len(sys.argv) > 1):
		dest =  sys.argv[1]
	else:
		print("Usage: python tabulate.py <destination_path> [prop_id_path]")
		return

	infile = open('all_ids.txt', 'r')
	picklefile = open('pgndict', 'r')
	dict = cPickle.load(picklefile)
	errorfile = open('invalid_ids.txt', 'w')
	if(len(sys.argv) > 2):
		prop_loc = sys.argv[2]
		propfile = open(prop_loc, 'w')
		propfile.write("| CAN ID | PGN | Proprietary |\n")
		propfile.write("| ------ | --- | ----------- |\n")
	else:
		propfile = errorfile

	for id in infile: #infile contains all the ids in a list
		id = id.strip().upper()
		pgn_hex = id[2:6]
		if(pgn_hex[0].upper() != 'F'):
			pgn_hex = pgn_hex[0:2] +"00"
		pgn = str(int(pgn_hex, 16))

		try:
			id_info = dict[pgn]
			# if this id is marked as proprietary, output it into the list of prop ids file
			if(id_info.description.split()[0] == 'Proprietary'):
				desc = id_info.description.split()
				description = desc[0]+" "+desc[1]
				propfile.write("| "+id+" | "+pgn+" | "+description+" |\n")
				continue
			outfile = open(dest+'/'+id+'.md', 'w')
			write_md(outfile, id_info, id)
			outfile.close()
		except KeyError:
			errorfile.write(id+" "+pgn+"\n")

	infile.close()
	picklefile.close()
	errorfile.close()

def write_md(outfile, id_info, id):
	outfile.write("---\n")
	outfile.write("layout: page\n")
	outfile.write("title: "+id+"\n")
	outfile.write("description: "+id_info.description+"\n")
	outfile.write("pgn: "+id_info.pgn+"\n")
	outfile.write("---\n\n")

	outfile.write("### Description\n\n")
	outfile.write(id_info.description+"\n\n")

	outfile.write("### ID Breakdown\n")
	outfile.write("* PGN: "+id_info.pgn +"\n")
	outfile.write("* Source Address: "+id[len(id)-2 : len(id)]+"\n")
	if(id[2] == 'F'):
		outfile.write("* Destination Address: (PS): "+id[len(id)-4 : len(id)-2]+"\n")
	outfile.write("* PDU Format (PF): "+id[len(id)-6 : len(id)-4]+"\n")
	outfile.write("* Data Page: b"+format(int(id[1:2], 16), "04b")[2:4]+"\n")
	outfile.write("* Priority: "+str(int(format(int(id[0:2], 16), "05b")[0:3],2))+"\n")

	outfile.write("### Data Packet Breakdown:\n\n")
	outfile.write("| Name | Size | Byte Offset |\n")
	outfile.write("| ---- | ---- | ----------- |\n")
	for attr in id_info.attributes:
		byte = attr.size.strip().split(" ")
		bytestring = byte[0]
		try:
			if(byte[1]=="byte" or byte[1] == "bytes"):
				bytestring+="B"
			elif(byte[1]=="bit" or byte[1]=="bits"):
				bytestring+="b"
		except IndexError:
			bytestring = "-"
		outfile.write("| "+attr.description)
		outfile.write(" | "+bytestring)
		outfile.write(" | "+attr.byte_offset.strip()+" |\n")

if __name__=="__main__":
	main()
