import sys

id = sys.argv[1][0:len(sys.argv[1])-4].split("/")[1]
dest = sys.argv[2]
infile = open(sys.argv[1], "r")
outfile = open(dest+"/"+id+".md", "w")
pgn_hex = id[2:6]

startfile = infile.tell()
line = infile.readline()
infile.seek(startfile)

description = line.split(",")[0]

outfile.write("---\n")
outfile.write("layout: page\n")
outfile.write("title: "+id+"\n")
outfile.write("description: "+description+"\n")
outfile.write("---\n\n")

outfile.write("### Description\n\n")
outfile.write(description+"\n\n")

outfile.write("### ID Breakdown\n")
outfile.write("<ul>\n")
outfile.write(" <li>PGN: "+pgn_hex +"</li>\n")
outfile.write(" <li>Source Address: "+id[len(id)-2 : len(id)]+"</li>\n")
outfile.write(" <li>Destination Address: (PS): "+id[len(id)-4 : len(id)-2]+"</li>\n")
outfile.write(" <li>PDU Format (PF): "+id[len(id)-6 : len(id)-4]+"</li>\n")
outfile.write(" <li>Data Page: b"+format(int(id[1:2], 16), "04b")[2:4]+"</li>\n")
outfile.write(" <li>Priority: "+str(int(format(int(id[0:2], 16), "05b")[0:3],2))+"</li>\n")
outfile.write("</ul>\n\n")

outfile.write("### Data Packet Breakdown:\n\n")
outfile.write("| Name | Size | Byte Offset |\n")
outfile.write("| ---- | ---- | ----------- |\n")
for i,line in enumerate(infile):
	args = line.split(",")
	byte = args[3].strip().split(" ")
	if(byte[1]=="byte" or byte[1] == "bytes"):
		byte[1]="B"
	elif(byte[1]=="bit" or byte[1]=="bits"):
		byte[1]="b"
	outfile.write("| "+args[2]+" | "+byte[0]+byte[1]+" | "+args[1].strip()+" |\n")
	#	           |  <name>     |  <n bytes>          |  <i.j byte offset>


