#
# Filter for Wireshark (tshark) captured data in text file format.
# Filters Layers 3,4 except for frames where multiple TCP Segments are Reassembled.
#
import sys
import re

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print "\nMissing input file name (*.txt).\n"
		sys.exit(1)
	fname = sys.argv[1]
	fp = open(fname, "r")
	lines = fp.readlines()
	fp.close()
	
	buff = []
	buffering = False
	
	for line in lines:
		str = line[:-1]
		v = re.search("^Frame \d+:", str)
		if v != None:
			for lp in buff:
				print lp
			print
			print " -"*50
			print
			print str
			buffering = False
			buff = []
		
		v = re.search("Hypertext Transfer Protocol", str)
		if v != None:
			buffering = True
			print
			
		v = re.search("TCP segment data \(", str)
		if v != None:
			buffering = True
			print
		
		if buffering:
			print str


