import os, sys

sourceDir = "/work/mypy/Wrappers/NEW_api_pseudo-code"

REST_CMDS = ['GET', 'PUT', 'POST', 'DELETE']
# REST_CMDS = ['DELETE']


fname = "/work/itest/Analy/data/Rest_ALL-Links-XRef-Array.dat"
fp = open(fname, "r")
lines = fp.readlines()
fp.close()

Dlink = {}

for line in lines:
	line = line [:-1]
	sline = line.split(",")
	key = sline[0].strip()
	link = sline[1].strip()
	name = sline[2].strip()
	Dlink[key] = link


Dcmds = {}

for restType in REST_CMDS:
	fname  = "/work/itest/Analy/data/Rest_%s-Commands-XRef-Array.dat" % restType
	fp = open(fname, "r")
	lines = fp.readlines()
	fp.close()

	for line in lines:
		line = line [:-1]
		sline = line.split(",")
		rkey = sline[0].strip()
		command = sline[1].strip()
		Dcmds[command] = rkey


fname = sys.argv[1]
fPath = "%s/%s.tcl" % ( sourceDir, fname )
fp = open(fPath, "r")
lines = fp.readlines()
fp.close()

COUNT_default_print = 0
COUNT_not_in_D = 0
COUNT_identified_cmd = 0
COUNT_identified_rest = 0

for line in lines:
	line = line [:-1]
	RestFound = False
	for rest in REST_CMDS:
		if rest in line:
			COUNT_identified_rest = COUNT_identified_rest + 1
			RestFound = True
			newRestLine = line.replace('"', '')
			sline = newRestLine.split()
			RestStr = sline[0] + " " + sline[1]
			if RestStr in Dcmds:
				COUNT_identified_cmd = COUNT_identified_cmd + 1
				keyLink = Dcmds[RestStr]
				url = Dlink[keyLink]
#				linkStr = '<a style="color:#dd0000; font-weight:bold; text-decoration:none" href="%s">%s</a>' % ( url, RestStr ) 
				linkStr = '<a style="color:#dd0000; font-weight:bold; text-decoration:none" href=javascript:newWin("%s")>%s</a>' % ( url, RestStr ) 

#  <a href='javascript:newWin("http://yahoo.com")'>Click Here</a>


				lpLine = newRestLine.replace(RestStr, linkStr)
				print "%s" % ( lpLine )
			else:
				print "%s    # Not in Dict" % RestStr
				COUNT_not_in_D = COUNT_not_in_D + 1

	if RestFound:
		RestFound = False
	else:
		print line
		COUNT_default_print = COUNT_default_print + 1
