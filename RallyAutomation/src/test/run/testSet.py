'''
Created on Nov 10, 2014

@author: ljiang
'''
import sys
#from pprint import pprint
#from testCase import *
#from testObject import *
#import datetime
#from user import *
#import user

import logging
#from rallyLogger import *



class testSet(object):
    '''
    classdocs
    '''
    def __init__(self, rally,data):
        '''
        Constructor
        '''
        self.data=data
        self.rally=rally
        #rallyLogger.setup("logging.json")
        self.logger = logging.getLogger(__name__)
        self.logger.propagate = False
    
           
    #Show a TestSet identified by the FormattedID value
    def getTSByID(self):
        try:
            
            query_criteria = 'FormattedID = "%s"' % str(self.data['ts']['FormattedID'])
            response = self.rally.get('TestSet', fetch=True, query=query_criteria)
            dic={}
            for ts in response:
                for key in dir(ts):
                    if not key.endswith("__"):
                        dic[key]=getattr(ts,key)
                    #print key,getattr(ts,key)
                break        
            #print "Test set obtained, ObjectID: %s  FormattedID: %s " % (ts.oid,ts.FormattedID)
            #print "--------------------------------------------------------------------"
            #pprint(dic)
            self.logger.debug("Test set obtained, ObjectID: %s, FormattedID: %s, Content: %s" % (ts.oid,ts.FormattedID,dic))
            return ts
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            self.logger.error('ERROR: %s \n' % details,exc_info=True)
            sys.exit(1)

    #Fetch all the test cases of specific test set
    def allTCofTS(self,ts):
        try:
            lst=[]
            #ts_obj=testSet(self.rally,self.data)
            #ts=ts_obj.getTSByID()       
            query_criteria = 'TestSets = "%s"' % str(ts._ref)
            response = self.rally.get('TestCase', fetch=True, query=query_criteria)
            for tc in response:
                lst.append(tc)
                #print "Test case obtained, ObjectID: %s  FormattedID: %s" % (tc.oid,tc.FormattedID)
                self.logger.debug("Test case obtained, ObjectID: %s  FormattedID: %s" % (tc.oid,tc.FormattedID))
            #self.logger.debug("The content of all test cases of test set %s is: %s" % (ts.FormattedID,lst))
            #pprint(lst)
            #print "--------------------------------------------------------------------"
            return lst
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            self.logger.error('ERROR: %s \n' % details,exc_info=True)
            sys.exit(1)

    
    #Update test set
    def updateTS(self):
        ts_data = self.data['ts']
        try: 
            ts = self.rally.post('TestSet', ts_data)  
            self.logger.debug("Test Set %s is updated" % ts.FormattedID)        
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            self.logger.error('ERROR: %s \n' % details)
            sys.exit(1)
        #print "Test Set %s updated" % ts.FormattedID
        #print "--------------------------------------------------------------------"
        return ts    
    
    #Update ScheduleState of Test Set 
    def updateSS(self,state):
        try:
            dic={}
            dic['ts']=self.data['ts'].copy()
            dic['ts'].pop('Build',None)
            if state == 0:
                dic['ts']['ScheduleState']="In-Progress"
            if state == 1:        
                dic['ts']['ScheduleState']="Accepted"
            if state == 2:
                dic['ts']['ScheduleState']="Completed"
            #ts_obj=testSet(self.rally,dic)
            #ts_obj.updateTS()
            self.data=dic.copy()
            self.updateTS()
            self.logger.debug("ScheduleState is successfully updated to %s" % dic['ts']['ScheduleState'])
        except Exception,details:
            self.logger.error('ERROR: %s \n' % details, exc_info=True)
            sys.exit(1)
    

    '''
    #Run the test set
    def runTS(self): 
        ts_obj=testSet(self.rally,self.data)
        ts=ts_obj.getTSByID()
        tcs=ts_obj.allTCofTS()
        to_obj=testObject(self.rally,self.data)
        tc_verds=to_obj.runTO() #run the actual tests for AVNext
        ur_obj=user(self.rally,self.data)   
        ur=ur_obj.getUser()
        trs=[]     
        for tc,verd in zip(tcs,tc_verds):
            if verd == 0:
                dic = {'TestCase':tc._ref,'Verdict':u'Fail','Build':self.data["ts"]["Build"],'Date':datetime.datetime.now().isoformat(),'TestSet':ts._ref,'Tester':ur._ref}      
            if verd == 1:
                dic = {'TestCase':tc._ref,'Verdict':u'Pass','Build':self.data["ts"]["Build"],'Date':datetime.datetime.now().isoformat(),'TestSet':ts._ref,'Tester':ur._ref}
            try:
                tr=self.rally.put('TestCaseResult', dic) 
                trs.append(tr)          
            except Exception, details:
                sys.stderr.write('ERROR: %s \n' % details)
                sys.exit(1)
            print "Test Case %s updated; Test result oid %s is created" % (tc.FormattedID,tr.oid)

        #Generate report
        filename="Report-%s.log" % datetime.datetime.now()
        try:
            with open(filename,"ab+") as f:
                for tr in trs:
                    f.write("Test Report:\nTest Case ID: %s\nBuild: %s\nVerdict: %s\nDate: %s\nTester: %s\n" % (tr.TestCase.FormattedID,tr.Build,tr.Verdict,tr.Date,tr.Tester.UserName))
        except Exception, details:
            sys.stderr.write('ERROR: %s \n' % details)
            sys.exit(1)
        print "Report %s is successfully generated" % filename        
        return trs
        
        
                           
                              
                    
                    
                     
                    
    
    #Create test case
    def createTC(self):
        tc_data = {key: value for key, value in self.data['tc'].items() if key is not 'FormattedID'} #Create a test case with all fields of data['tc'] except the key value pair of 'FormattedID'
        try:
            tc = self.rally.put('TestCase', tc_data)
        except Exception, details:
            sys.stderr.write('ERROR: %s \n' % details)
            sys.exit(1)
        print "Test case created, ObjectID: %s  FormattedID: %s" % (tc.oid, tc.FormattedID)      
        return tc  
        
    #Update test case
    def updateTC(self):
        tc_data = self.data['tc']
        try: 
            tc = self.rally.post('TestCase', tc_data)          
        except Exception, details:
            sys.stderr.write('ERROR: %s \n' % details)
            sys.exit(1)
        print "Test Case %s updated" % tc.FormattedID
        return tc
    
    #Delete test case
    def delTC(self):
        try: 
            delete_success=self.rally.delete('TestCase', self.data['tc']['FormattedID'])
        except Exception, details:
            sys.stderr.write('ERROR: %s %s %s does not exist\n' % (Exception,details,self.data['tc']['FormattedID']))
            sys.exit(1)
        if delete_success == True:
            print "Test case deleted, FormattedID: %s" % self.data['tc']['FormattedID']        
    '''