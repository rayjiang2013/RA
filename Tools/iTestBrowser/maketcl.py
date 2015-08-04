import os, sys, re
from iStructs import WrapperArgs

wPath  = '/work/mypy/Wrappers'
tcPath = '/work/itest/Analy/test_cases_all'

ITEM_GUID    = '<item guid='
ITEM_NAME    = '<item name='
ITEM_ACTIONID    = '<item actionId='
ITEM_TRANSFER    = '<item transferableToolId='

GUID        = 'action="eval">'
STEPS        = 'steps>'
CMD            = 'command>'
APP_PROPS    = 'EmptyPropertyGroup'     # "/>'
USE_FIELDS    = '<useFieldsInCommand>fals'
ITEM        = 'X_i_tem>'

NESTED        = '<nestedSteps>'
UNNESTED    = '</nestedSteps>'
OPEN_BRKT    = '{'
CLOSE_BRKT    = '}'
ARGS        = '<arguments>'
UNARGS        = '</arguments>'
UNITEM        = '</item>'

GET            = 'GET'
PUT            = 'PUT'
POST           = 'POST'
DELETE         = 'DELETE'

JSON_ADD    = 'addJsonNode'
JSON_GET    = 'getJsonNode'
JSON_DEL    = 'deleteJsonNode'
JSON_SETVAL    = 'setJsonValue'
JSON_GETVAL    = 'getJsonValue'

IO_OPEN     = 'open'
IO_WRITE    = 'write'
IO_GET_FILE = 'GetFile'


OP_RETURN    = 'return'
OP_FOR      = 'for'
OP_COMMENT  = 'comment'
OP_SLEEP 	= 'sleep'
OP_WHILE    = 'while'

ADM_GET_USER       = ''
ADM_GET_LICENSES       = ''
ADM_GET_ABOUT       = ''


NA_LIST     = [GUID, STEPS, CMD, APP_PROPS, USE_FIELDS, ITEM]
RESTCMDS     = [GET, PUT, POST, DELETE]
SINGLE_PARAM_CMDS = [JSON_ADD, JSON_GET, JSON_DEL, JSON_SETVAL, JSON_GETVAL, IO_OPEN, IO_WRITE, OP_RETURN, OP_FOR, OP_COMMENT, OP_SLEEP, OP_WHILE, IO_GET_FILE, ADM_GET_USER, ADM_GET_LICENSES, ADM_GET_ABOUT ]

WRAPPER_TOKEN    = "WRAPPER_FUNC "
JSON_TOKEN        = "JSON_FUNC "
REST_TOKEN        = "REST_CALL "

DEBUG = False

Wrappers = WrapperArgs.keys()


def getArgs(lines):
    theseArgs = []
    try:
        startArgs = lines.index(ARGS) + 1
    except:
        return theseArgs
        
    endArgs   = lines.index(UNARGS)
    argLines = lines[startArgs:endArgs]
    lastVar = ''
    for line in argLines:
        v = re.match("<isMandatory>(.*)<.*", line)
        if v != None:
            if lastVar != '':
                theseArgs.append(lastVar)
                lastVar = ''
            mLine = v.group(1)
            theseArgs.append("isMandatory=%s" % mLine)
            continue

        v = re.match("<item name=\"(.*)\"[/]*>", line)
        if v != None:
            mLine = v.group(1)
            lastVar = mLine
            continue

        v = re.match("<defaultValue>(.*)</defaultValue>", line)
        if v != None:
            mLine = v.group(1)
            theseArgs.append("%s=%s" % (lastVar, mLine))
            lastVar = ''
            continue

    if lastVar != '':
        theseArgs.append(lastVar)

    return theseArgs


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "\nUsage:\npython maketcl.py < -tc | -api > <function_name[.fftc]>\n\n"
        sys.exit(1)

    wType = sys.argv[1]
    wName = sys.argv[2]
    
    thePath = ''
    if wType == '-tc':
        thePath = tcPath
    elif wType == '-api':
        thePath = wPath
    else:
        print "\nUsage:\npython maketcl.py < -tc | -api > <function_name[.fftc]>\n\n"
        sys.exit(1)

    if not wName.endswith(".fftc"):
        wName = wName + ".fftc"

    wFile = "%s/%s" % ( thePath, wName )
    fp = open(wFile, 'r')
    lines = fp.readlines()
    fp.close()

    scriptLines = []
    wrappers_used = []
    tmpLines = []
    Args = []
    Skip = False

    for line in lines:
        for token in NA_LIST:
            if token in line:
                Skip = True
                break

        if not Skip:
            tmpLines.append(line.strip())
        Skip = False

    listArgs = getArgs(tmpLines)
    strArgs = ", ".join(listArgs)

    for line in tmpLines:
        v = re.match(".*<item name=\"(.*)\" isPublic=\"true.*", line)
        if v != None:
            mLine = v.group(1)
            sLine = mLine.replace("&quot;", "\"")
            scriptLines.append("proc %s { %s }  {" % (sLine, strArgs))
            continue

        v = re.match(".*<body>(.*)</body>", line)
        if v != None:
            mLine = v.group(1)
            sLine = mLine.replace("&quot;", "\"")
            scriptLines.append(sLine)
            continue

        v = re.match(".*<item guid=.* action=\"(.*)\" .*", line)
        if v != None:
            mLine = v.group(1)

            if mLine in Wrappers:
                wrappers_used.append(mLine)

            sLine = mLine.replace("&quot;", "\"")
            scriptLines.append(sLine)
            continue

        v = re.match(".*<item guid=.* action=\"(.*)\".*", line)
        if v != None:
            mLine = v.group(1)
            sLine = mLine.replace("&quot;", "\"")

            scriptLines.append(sLine)
            continue

        v = re.match(".*<nestedSteps>", line)
        if v != None:
            scriptLines.append(OPEN_BRKT)
            continue

        v = re.match(".*<\/nestedSteps>", line)
        if v != None:
            scriptLines.append(CLOSE_BRKT)
            continue

        v = re.match(".*<applicationProperties.*restful.RESTfulInvoke.* action=(.*) action.*", line)
        if v != None:
            mLine = v.group(1)
            sLine = mLine.replace("&quot;", "\"")
            scriptLines.append(sLine)

            v = re.match(".*<applicationProperties.*restful.RESTfulInvoke.* message=(.*) message.*", line)
            if v != None:
                mLine = v.group(1)
                sLine = mLine.replace("&quot;", "\"")
                sLine = "#  message=%s" % sLine
                scriptLines.append(sLine)
            continue

    scriptLines.append(CLOSE_BRKT)
    

    #-------------------------------------------------------------------------------------------
    #
    #    Another pass to merge lines together for CONTORL cmds: if, call, foreach, etc
    #
    q = 0
    while( q >= 0 ):
        try:
            q = scriptLines.index("foreach")
            forLine = "%s { %s }  {" % (scriptLines[q], scriptLines[q+1] )
            scriptLines[q] = forLine
            scriptLines.pop(q+2)
            scriptLines.pop(q+1)
        except:
            q = -1

    q = 0
    while( q >= 0 ):
        try:
            q = scriptLines.index("if")
            ifLine = "%s { %s }  {" % (scriptLines[q], scriptLines[q+1] )

            scriptLines[q] = ifLine
            scriptLines.pop(q+4)
            scriptLines.pop(q+3)
            scriptLines.pop(q+2)
            scriptLines.pop(q+1)


            for k in range(q+1, len(scriptLines)-1):
                if scriptLines[k] == CLOSE_BRKT:
                    scriptLines.pop(k)
                    break
        except:
            q = -1


    q = 0
    while( q >= 0 ):
        try:
            q = scriptLines.index("elseif")
 
            for k in range(q+1, len(scriptLines)-1):
                if scriptLines[k] == CLOSE_BRKT:
                    scriptLines.pop(k)
                    break

            ifLine = "%s { %s }  {" % (scriptLines[q], scriptLines[q+1] )
            scriptLines[q] = CLOSE_BRKT            # close previous 'if' block
            scriptLines[q+1] = ifLine
            scriptLines.pop(q+2)

        except:
            q = -1


    q = 0
    while( q >= 0 ):
        try:
            q = scriptLines.index("else")
 
            for k in range(q+1, len(scriptLines)-1):
                if scriptLines[k] == CLOSE_BRKT:
                    scriptLines.pop(k)
                    break

            elseLine = "%s  {" % scriptLines[q]
            scriptLines[q] = CLOSE_BRKT            # close previous 'if' block
            scriptLines[q+1] = elseLine

        except:
            q = -1


    for rest in RESTCMDS:
        q = 0
        while( q >= 0 ):
            try:
                q = scriptLines.index(rest)
                restCall   = scriptLines[q]
                restParams = scriptLines[q+1]
                restLine = "%s %s" % ( restCall, restParams )
                scriptLines[q] = restLine
                scriptLines.pop(q+1)
            except:
                q = -1

    for wrapper in wrappers_used:
        q = 0
        while( q >= 0 ):
            try:
                q = scriptLines.index(wrapper)
                paramLine = scriptLines[q+1]
                
                if paramLine.startswith("-"):
                    restLine = "%s %s" % (scriptLines[q], paramLine )
                    scriptLines[q] = restLine
                    scriptLines.pop(q+1)
                else:
                    q = -1
            except:
                q = -1

    for json in SINGLE_PARAM_CMDS:
        q = 0
        while( q >= 0 ):
            try:
                q = scriptLines.index(json)
                jsonParams = scriptLines[q+1]
                jsonLine = "%s %s" % (scriptLines[q], jsonParams )
                scriptLines[q] = jsonLine
                scriptLines.pop(q+1)
            except:
                q = -1

    q = 0
    while( q >= 0 ):
        try:
            q = scriptLines.index("call")
            callLine = "%s %s" % (scriptLines[q], scriptLines[q+1] )
            scriptLines[q] = callLine
            scriptLines.pop(q+1)
        except:
            q = -1

    tabs = 0

    for line in scriptLines:
        line = line.replace("&amp;", "&")
        line = line.replace("&gt;", ">")
        line = line.replace("&lt;", "<")
        line = line.replace("%5B", "[")
        line = line.replace("%5D", "]")
        if line == CLOSE_BRKT:
            print "\t"*(tabs-1),
        else:
            if tabs > 0:
                print "\t"*tabs,
        print "%s" % line
        en_tabs = line.count(OPEN_BRKT)
        en_tabs = en_tabs - line.count("\{")

        de_tabs = line.count(CLOSE_BRKT)
        de_tabs = de_tabs - line.count("\}")
        tabs = tabs + (en_tabs - de_tabs)
        if tabs < 0:
            tabs = 0

