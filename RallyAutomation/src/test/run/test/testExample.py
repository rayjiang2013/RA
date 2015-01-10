from src.test.run.testObject import testObject
#import src.test.run.example
#import pytest
import sys

from pyrallei import Rally, rallyWorkset #By using custom package pyrallei as a workaround for the bug: bug: https://github.com/RallyTools/RallyRestToolkitForPython/issues/37
import json


def setup_module(module):
    try:
        options = ['--config=../config.cfg'] #--config=config.cfg "extra.cfg"
        server, user, password, apikey, workspace, project = rallyWorkset(options) #apikey can be obtained from https://rally1.rallydev.com/login/
        #print "--------------------------------------------------------------------\nRally project info is as below:"
        #print " ".join(['|%s|' % opt for opt in [server, user, password, apikey, workspace, project]])
        #print "--------------------------------------------------------------------"
        global rally
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
        global data
        # Read other configuration parameters from the extra.json
        with open('../extra.json') as data_file:    
            data = json.load(data_file)
            #print "The extra.json configuration file contains parameters as below:"
            #print "--------------------------------------------------------------------"   
            

    except Exception,details:
        sys.exit(1)
        print details
    
#def teardown_module(self):
        

def test_testobject_copyts():
    to=testObject(rally,data)
    ts_new=to.copyTS()   
    assert ts_new.FormattedID==data["ts"]["FormattedID"]  