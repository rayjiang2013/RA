'''
Created on Nov 10, 2014

@author: ljiang
'''
import sys
from pprint import pprint
from testCase import *
from testObject import *
import datetime
from user import *

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
                    print key,getattr(ts,key)
                break        
            print "Test case obtained, ObjectID: %s  FormattedID: %s  Content: " % (ts.oid,ts.FormattedID)
            pprint(dic)
            return ts
        except Exception, details:
            sys.stderr.write('ERROR: %s \n' % details)
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
                print "Test case obtained, ObjectID: %s  FormattedID: %s" % (tc.oid,tc.FormattedID)
            pprint(lst)
            return lst
        except Exception, details:
            sys.stderr.write('ERROR: %s \n' % details)
            sys.exit(1)

    
    #Update test set
    def updateTS(self):
        ts_data = self.data['ts']
        try: 
            ts = self.rally.post('TestSet', ts_data)          
        except Exception, details:
            sys.stderr.write('ERROR: %s \n' % details)
            sys.exit(1)
        print "Test Folder %s updated" % ts.FormattedID
        return ts    
    
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