import os, sys, re

# fname = '/work/itest/Analy/RestAPI.fftc'
fname = '/Users/rcollazo/Downloads/RestAPITest/Utilities/RestAPI.fftc'

if __name__ == '__main__':
	print "\n"
	fp = open(fname, 'r')
	lines = fp.readlines()
	fp.close()
	
	tmpLines = []
	Args = []
	Skip = False
	fCount = 0
	
	fp = open("junkfile", "w")

	for line in lines:
		v = re.match(".*<item name=\"(.*)\" isPublic=\"true.*", line)
		if v != None:
			wName = v.group(1)
			fName = "WrappersTEMP_NEW/%s.fftc" % wName
			print "\n"
			print "-"*100
			fCount = fCount + 1
			print "\nOpening New File (%d): %s\n" % (fCount, fName)
			fp.close()
			fp = open(fName, "w")

		print line[:-1]
		fp.write(line)
		
	fp.close()
	
