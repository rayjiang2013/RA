'''
Created on Oct 28, 2014

@author: ljiang
'''
import sys

from pyrallei import Rally, rallyWorkset #By using custom package pyrallei as a workaround for the bug: bug: https://github.com/RallyTools/RallyRestToolkitForPython/issues/37
import json
from testObject import testObject
from rallyLogger import *
import inspect
import os

#The main function    
if __name__ == '__main__':
    #Setup
    try:
        #logConfig("logging.json")
        setup(sys.argv[3])
        logger = logging.getLogger(__name__)
        logger.propagate=False
                
        options = [opt for opt in sys.argv[1:] if opt.startswith('--')]
        server, user, password, apikey, workspace, project = rallyWorkset(options) #apikey can be obtained from https://rally1.rallydev.com/login/
        #print "--------------------------------------------------------------------\nRally project info is as below:"
        logger.debug("Rally project info is as below:\n %s" % " ".join(['|%s|' % opt for opt in [server, user, password, apikey, workspace, project]]))
        #print " ".join(['|%s|' % opt for opt in [server, user, password, apikey, workspace, project]])
        #print "--------------------------------------------------------------------"
        rally = Rally(server, user, password, workspace=workspace, project=project)
        rally.enableLogging('rally.example.log', attrget=True, append=True)
        #tstep,tcid,tcoption,tf=sys.argv[-4:]
        '''
        # Read other configuration parameters from the extra.cfg 
        para={}
        with open(sys.argv[-1],"r") as f:
            for line in f:
                line=line.replace("\n","")
                words=line.split(":",)
                para[words[0]]=words[1]
        for key,value in para.items():
            print key+":"+value   
        '''
        
        # Read other configuration parameters from the extra.json
        with open(sys.argv[2]) as data_file:    
            data = json.load(data_file)
            #print "The extra.json configuration file contains parameters as below:"
            logger.debug("The extra.json configuration file contains parameters as below: %s" % data)
            #print "--------------------------------------------------------------------"    
    except Exception,details:
        #x=inspect.stack()
        if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
            raise
        else:
            #print Exception,details
            logger.error('ERROR: %s \n' % details,exc_info=True)
            sys.exit(1)

    to=testObject(rally,data)
    to.getLatestBuild()
    ts_ut=to.copyTS()
    (verd,newdt)=to.runTO(ts_ut)
    test_results=to.runTS(verd,newdt)    
    report=to.genReport(test_results)
    to.sendNotification(report)
    

    

