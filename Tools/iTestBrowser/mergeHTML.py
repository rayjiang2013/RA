import os, sys

#
# <a href="itest_actions/System/GetSystemAbout.fftc.html" target="frame2">GetSystemAbout.fftc</a><br>
#

# SOURCE_DIR_1 = "/work/mypy/Wrappers/itest_params_v1-KEEP"
SOURCE_DIR_1 = "/work/mypy/Wrappers/itest_params_062615"
SOURCE_DIR_2 = "/work/mypy/Wrappers/NEW_api_pseudo-code_html"

###  see .sh   TARGET_DIR   = "/work/mypy/Wrappers/HERO_test_params"

LAST_LINE = "</table></p><br></body></html>"

fname = sys.argv[1]
fpath = "%s/%s.html" % ( SOURCE_DIR_1, fname )

########D = {}

try:
#	print ">>>%s<<< \n" % fpath
	fp = open(fpath, "r")
	lines = fp.readlines()
	fp.close()
	
	for i in range(0, len(lines)-2):
		line = lines[i][:-1]
		print line

 	lastLine = lines[len(lines)-1][:-1]
 	newLines = []

	if lastLine.startswith("</table>"):
		fpath = "%s/%s.html" % ( SOURCE_DIR_2, fname )
		fp = open(fpath, "r")
		newLines = fp.readlines()
		fp.close()
		
		print "</table></p><br><br><center>"
		print "<table border=1 bgcolor=#ececec cellspacing=0 cellpadding=24 width=93% style='font-size:8pt; font-family: Calibri; font-weight:normal'><tr><td><code style='line-height:16px'>"
		for line in newLines:
			print line[:-1]
		print "</code></td></tr></table><br></body></html>"

	else:
		print ">>>>>>>>>>>>>>>>>>>>>>>>>  ERROR processing: %s" % fname

except:
	print ">>>>>>>>>>>>>>>>>>>>>>>>>  ERROR I/O?: %s" % fname




# 		offs = line.find("frame2") + 8
# 		eow  = line.find("fftc<")



# try:
# 	fp = open(fname, "r")
# 	lines = fp.readlines()
# 	fp.close()
# 
# 	print lines[len(lines)-1][:-1],
# 	print "\t\t\t%s" % fname
# except:
# 	print ">>>>>>>>>>>>>>>>>>>>>>>>>  ERROR opening: %s" % fname


