'''
Created on Nov 5, 2014

@author: ljiang
'''

import sys
#from pprint import pprint
#from testCase import *
from testCase import testCase
import logging
#from logging import config
import inspect


class testCaseStep:
    '''
    This is the class module for test case    
    '''
    def __init__(self, rally,data):
        '''
        Constructor
        '''
        self.data=data
        self.rally=rally
        self.logger = logging.getLogger(__name__)
        self.logger.propagate=False
    
    #Show a TestCase identified by the FormattedID value
    def getTCStepByID(self):
        try:
            tc_obj=testCase(self.rally,self.data)
            tc=tc_obj.getTCByID()
            #query_criteria_tc = 'FormattedID = "%s"' % str(self.data['tc']['FormattedID'])
            #tc_response = self.rally.get('TestCase', fetch=True, query=query_criteria_tc)
            lst=[]
            #for tc in tc_response:  
            query_criteria_ts = 'TestCase = "%s"' % str(tc.ref)
            ts_response=self.rally.get('TestCaseStep', fetch=True, query=query_criteria_ts)                          
            for ts in ts_response:
                dic={}
                for key in dir(ts):                            
                    if not key.endswith("__"):
                        dic[key]=getattr(ts,key)   
                lst.append(dic)
            #pprint(lst)                    
            #print "Test case step obtained, FormattedID: %s, Content: %s" % (str(self.data['tc']['FormattedID']))
            self.logger.debug("Test case step obtained, FormattedID: %s, Content: %s" % (str(self.data['tc']['FormattedID']),lst))
            return ts
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
         
    
    #Create test case step
    def createTCStep(self):
        #tc_data = {key: value for key, value in self.data['tc'].items() if key is not 'FormattedID'} #Create a test case with all fields of data['tc'] except the key value pair of 'FormattedID'
        try:
            tc_obj=testCase(self.rally,self.data)
            tc=tc_obj.getTCByID()
            testcasestep_fields={}
            for i in range(len(self.data['tcstep'])):
                testcasestep_fields = self.data['tcstep'][i]
                testcasestep_fields['TestCase']=tc.ref
                testcasestep = self.rally.put('TestCaseStep', testcasestep_fields)
                #print "===> Created  TestCaseStep: %s   OID: %s" % (testcasestep.StepIndex, testcasestep.oid)    
                self.logger.debug("===> Created  TestCaseStep: %s   OID: %s" % (testcasestep.StepIndex, testcasestep.oid))
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
'''       
    #Update test case step
    def updateTCStep(self):
        tc_data = self.data['tc']
        try: 
            tc = self.rally.post('TestCase', tc_data)          
        except Exception, details:
            sys.stderr.write('ERROR: %s \n' % details)
            sys.exit(1)
        print "Test Case %s updated" % tc.FormattedID
        return tc
   
    #Delete test case
    def delTCStep(self):
        try: 
            delete_success=self.rally.delete('TestCase', self.data['tc']['FormattedID'])
        except Exception, details:
            sys.stderr.write('ERROR: %s %s %s does not exist\n' % (Exception,details,self.data['tc']['FormattedID']))
            sys.exit(1)
        if delete_success == True:
            print "Test case deleted, FormattedID: %s" % self.data['tc']['FormattedID']
'''            

    
        