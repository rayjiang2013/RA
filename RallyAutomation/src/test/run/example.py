'''
Created on Oct 28, 2014

@author: ljiang
'''
import inspect
import sys

from pyral import Rally,rallyWorkset #The bugs  https://github.com/RallyTools/RallyRestToolkitForPython/issues/37 and https://github.com/RallyTools/RallyRestToolkitForPython/issues/40 should be fixed according comments from the po. Switch back to Pyral from now on. 
#from pyrallei import Rally, rallyWorkset #By using custom package pyrallei as a workaround for the bug: bug: https://github.com/RallyTools/RallyRestToolkitForPython/issues/37
import json
from testObject import testObject
from rallyLogger import *

import os
from buildDefinition import buildDefinition
from build import build
from copy import deepcopy

from extractAPI import extractAPI
import constants

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
        rally = Rally(server, user, password, apikey=apikey,workspace=workspace, project=project)#include apikey=apikey to workaround http://stackoverflow.com/questions/30495164/getting-error-rallyrestapierror-422-not-authorized-to-perform-action-invalid and http://stackoverflow.com/questions/30492008/net-rally-restapi-error-not-authorized-to-perform-action-invalid-key-when-cr
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
   
        #api_obj=extractAPI(rally,data)

        
        to_obj=testObject(rally,data)
        
        if to_obj.sanityCheck(data['ts']['FormattedID']):
            to_obj.updateBuildInfo()
            to_obj.getLatestBuild()
            ts_ut=to_obj.copyTS()
            (verd,newdt)=to_obj.runTO(ts_ut)
            test_results=to_obj.runTS(verd,newdt)    
            report=to_obj.genReport(test_results,constants.FROM_TR)
            to_obj.sendNotification(report)

        else: 
            pass
            #raise Exception('Environment sanity check failed')            
        
        
        
    except Exception,details:
        #x=inspect.stack()
        #print ('test_' in x[1][3])
        #if ('test_' in inspect.stack()[1][3]) or ('test_' in inspect.stack()[2][3]):
            #raise
        #else:
            #print Exception,details
        logger.error('ERROR: %s \n' % details,exc_info=True)
        sys.exit(1)

    

