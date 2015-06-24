#
#
# Filter for Wireshark (tshark) captured data in text file format.
# Provides single line summary for HTTP frames.
# Kludgy but convenient extraction of Hex Dump formated 
#
import os, sys, re

MAX_LINES = 41000

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print "\nMissing input file name.\n"
		sys.exit(1)
	FNAME = sys.argv[1]

	wFile = "%s" % ( FNAME )
	fp = open(wFile, 'r')
	lines = fp.readlines()
	fp.close()
	
	print "Lines read: %d\n" % len(lines)

	scriptLines = []
	wrappers_used = []
	tmpLines = []
	Args = []
	Skip = False
	DumpingResponse = False

	k = 0

	try:	
		for i in range(len(lines)):
			k = k + 1

			# exit on MAX_LINES reached - due to (currently) un-deterministic use of stack/pop()
			if k > MAX_LINES:
				print "k exceeds MAX_LINES (%d) ...   aborting\n." % MAX_LINES
				sys.exit(1)
			
			line = lines[i]
			line = line[:-1]
			v = re.match("^No\.     Time.*", line)
			if v != None:
				newFrame = line
				frameSummary = lines.pop(i+1)
				print 
				print newFrame
				print frameSummary[:-1]
				continue

			v = re.match("^Hypertext Transfer Protocol.*", line)
			if v != None:
				restCmd = lines.pop(i+1)
				if DumpingResponse:
					DumpingResponse = False
					print "\n"
				print restCmd[:-1]
				continue

			v = re.match("^[0-9a-f]{4}.*", line)
			if v != None:
				DumpingResponse = True
				dataLine = line[56:]
				sys.stdout.write(dataLine)
				continue
	except IndexError, e:
		print "\n>>>>>>>>>>    End of Processing. \n\n"
		sys.exit(0)

