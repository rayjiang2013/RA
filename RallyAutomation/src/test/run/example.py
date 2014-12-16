'''
Created on Oct 28, 2014

@author: ljiang
'''
import sys

from pyrallei import Rally, rallyWorkset #By using custom package pyrallei as a workaround for the bug: bug: https://github.com/RallyTools/RallyRestToolkitForPython/issues/37
#from pprint import pprint
import json
#from test.run.testCase import *
#from test.run.testCaseStep import *
#from test.run.testFolder import *
#from test.run.testSet import *
from testObject import testObject
#import logging
#from logging import config
from rallyLogger import *
#from testSet import testSet
#from defect import defect

#from testCase import testCase
#from testCaseResult import testCaseResult
#logger = logging.getLogger(__name__)
#logger.propagate=False
'''
#Fetch test cases 
def fetch_tc(rally,num,tcid):
    #Fetch all the test cases 
    testcases=None
    if num == "0":    
        testcases = rally.get('TestCase',fetch=True)
        print testcases
    #Fetch one specific test case
    elif num == "1":
        query_criteria = 'FormattedID = "%s"' % tcid
        #query_criteria_2 = 'Name = "Switching from v6 protocol to v4 protocol when session is up (active side)"'
        testcases = rally.get('TestCase', fetch=True, query=query_criteria) #query is not working: bug: https://github.com/RallyTools/RallyRestToolkitForPython/issues/37
        print testcases
    return testcases

#Fetch all the fields of specific test cases of specific test run(folder)
def all_tc_of_tf(testcases,testfolder):
    lst=[]
    for tc in testcases:
        if tc.TestFolder!=None:
            if tc.TestFolder.Name == testfolder:
                dic={}
                for key in dir(tc):
                    if not key.endswith("__"):
                        dic[key]=getattr(tc,key)
                        print key,getattr(tc,key)
                lst.append(dic)
                break           
    print lst


#Show a TestCase identified by the FormattedID value. 
#From the the Rally RESTFUL api:https://rally1.rallydev.com/slm/doc/webservice/ if we query all test cases, it will return 741
#records. However, if use pyral or just view it on https://rally1.rallydev.com/#/18139290329d/testcases?tpsV=qv%3A0 , there are only 654
#test cases. The test cases 1, 3-7, 9-96 are all missing. I guess the admin of Rally has set up some permission or what to forbid viewer to view it.
#Ex: try query - (FormattedID = "TC25")

def tc_by_id(testcases,fmid):
    #lst=[]
    #s=unicode(fmid)
    dic={}
    for tc in testcases:
        s1=tc.FormattedID.encode('ascii','ignore')
        if s1==fmid:
            for key in dir(tc):
                if not key.endswith("__"):
                    dic[key]=getattr(tc,key)
                    print key,getattr(tc,key)
            break
    pprint(dic)
    
#Create test case
def create_tc(rally,data):
    proj = rally.getProject()
    users = rally.getAllUsers()
    user = rally.getUserInfo(username='lei.jiang@spirent.com').pop(0)
#    tcs = fetch_tc(rally,0,"")
    print users #bug found in https://github.com/RallyTools/RallyRestToolkitForPython/issues/40
    print proj 
    print user
    tc_data = {key: value for key, value in data['tc'].items() if key is not 'FormattedID'} #Create a test case with all fields of data['tc'] except the key value pair of 'FormattedID'
    try:
        tc = rally.put('TestCase', tc_data)
    except Exception, details:
        sys.stderr.write('ERROR: %s \n' % details)
        sys.exit(1)
    print "Test case created, ObjectID: %s  FormattedID: %s" % (tc.oid, tc.FormattedID)

#Update test case
def update_tc(rally,data):
    tc_data = data['tc']
    try: 
        tc = rally.post('TestCase', tc_data)          
    except Exception, details:
        sys.stderr.write('ERROR: %s \n' % details)
        sys.exit(1)
    print "Test Case %s updated" % tc.FormattedID
    return tc

#Update test case step
def create_tc_step(tc,data):
    testcasestep_fields={}
    for i in range(len(data['tcstep'])):

        testcasestep_fields = {
            "TestCase"          : tc.ref,
            "StepIndex"         : i,
            "Input"             : data['tcstep'][i]['Input'],
            "ExpectedResult"    : data['tcstep'][i]['ExpectedResult']
        }

        testcasestep_fields = data['tcstep'][i]
        testcasestep_fields['TestCase']=tc.ref
        testcasestep = rally.put('TestCaseStep', testcasestep_fields)
        print "===> Created  TestCaseStep: %s   OID: %s" % (testcasestep.StepIndex, testcasestep.oid)    

#Delete test case
def del_tc(data):
    try: 
        delete_success=rally.delete('TestCase', data['tc']['FormattedID'])
    except Exception, details:
        sys.stderr.write('ERROR: %s %s %s does not exist\n' % (Exception,details,data['tc']['FormattedID']))
        sys.exit(1)
    if delete_success == True:
        print "Test case deleted, FormattedID: %s" % data['tc']['FormattedID']
'''
'''
#To log   
def logConfig(log_config):

    #root = logging.getLogger('')
    try:
        with open(log_config, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
        logger.propagate = False
        logger.debug("The logging configuration is successfully loaded")
    except Exception,details:
        logger.error('ERROR: %s \n' % details, exc_info=True)
        sys.exit(1)
    #root.disabled=True
    #handler = logging.FileHandler('rally-automation-framework-%s.log' % datetime.datetime.now())
        
        
    #logger.addHandler(handler)

    #logger.info('Hello baby')
    #logger.debug('This is debugging message')
    #logger.error('This is an error')
        
    #root.info('Hello baby')
    #root.debug('This is debugging message')
    #root.error('This is an error')
'''

    
if __name__ == '__main__':
    #Setup
    try:
        #logConfig("logging.json")
        setup("logging.json")
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
        with open('extra.json') as data_file:    
            data = json.load(data_file)
            #print "The extra.json configuration file contains parameters as below:"
            logger.debug("The extra.json configuration file contains parameters as below: %s" % data)
            #print "--------------------------------------------------------------------"    
    except Exception,details:
            logger.error('ERROR: %s %s \n' % (Exception,details), exc_info=True)
            sys.exit(1)
    #tcases=fetch_tc(rally,data['tcoption'],data['tc']['FormattedID'])    
    #all_tc_of_tf(tcases,data['tf'])
    #tc_by_id(tcases,data['tc']['FormattedID']))
    #create_tc(rally,data)
    #tc=update_tc(rally,data)
    #create_tc_step(tc,data)
    #del_tc(data)
    #tc=testCase(rally,data)
    #tc.getTCByID()
    #tc.createTC()
    #tc.updateTC()
    #tc.delTC()
    #ts=testCaseStep(rally,data)
    #ts.getTCStepByID()
    #ts.createTCStep()
    #tf=testFolder(rally,data)
    #tf.getTFByID()
    #tf.delTF()
    #tf.addTC()
    #ts=testSet(rally,data)    
    #ts.createTS()
    #ts.copyTS()
    #ts.addTCs()
    #data['ts']['FormattedID']=
    #df=defect(rally,data)
    #df.getDFByID()
    #df.createDF()
    #tcr=testCaseResult(rally,data)
    #tc=testCase(rally,data)
    #tcr.allTCRofTC(tc.getTCByID())
    
    to=testObject(rally,data)
    ts_ut=to.copyTS()
    verd=to.runTO(ts_ut)
    test_results=to.runTS(verd)    
    report=to.genReport(test_results)
    to.sendNotification(report)
    
    #to_obj=testObject(None,None)    
    #to_obj.log("logging.json")

    

