'''
Created on Nov 12, 2014

@author: ljiang
'''
import sys
#from pprint import pprint

import logging
#from logging import config
import inspect


class testCaseResult:
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
        
    #Create test case
    def createTCResult(self):
        try:
            tr = self.rally.put('TestCaseResult', self.data['tcresult'])
            self.logger.debug("Test Case %s updated; Test result oid %s is created" % (tr.TestCase.FormattedID,tr.oid))
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
        #print "Test Case %s updated; Test result oid %s is created" % (tr.TestCase.FormattedID,tr.oid)     
        return tr  
    
    #Fetch all the test cases results of specific test case
    def allTCRofTC(self,tc):
        try:
            lst=[]
            #ts_obj=testSet(self.rally,self.data)
            #ts=ts_obj.getTSByID()       
            query_criteria = 'TestCase = "%s"' % str(tc._ref)
            response = self.rally.get('TestCaseResult', fetch=True, query=query_criteria)
            for tcr in response:
                lst.append(tcr)
                #print "Test case obtained, ObjectID: %s  FormattedID: %s" % (tc.oid,tc.FormattedID)
                self.logger.debug("Test case result obtained, ObjectID: %s  test case id: %s" % (tcr.oid,tc.FormattedID))
            #self.logger.debug("The content of all test cases of test set %s is: %s" % (ts.FormattedID,lst))
            #pprint(lst)
            #print "--------------------------------------------------------------------"
            return lst
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)

    #Delete test case result
    def delTCR(self):
        try: 
            delete_success=self.rally.delete('TestCaseResult', self.data['tcresult']['oid'])
        except Exception, details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s %s Test Case Result %s does not exist\n' % (Exception,details,self.data['tcresult']['oid']), exc_info=True)
                sys.exit(1)            
        if delete_success == True:
            self.logger.debug("Test case result deleted, ObjectID: %s" % self.data['tcresult']['oid'], exc_info=True)

            
    '''        
    #Update test case result
    def updateTCR(self):
        try: 
            tcr_data = {key: value for key, value in self.data['tcr'].iteritems() if ((key == u'Name') or (key == u'ScheduleState') or (key == u'Project') or (key == u'Description') or (key == u'Owner') or (key == u'Ready') or (key == u'Release') or (key == u'PlanEstimate') or (key == u'Blocked') or (key == u'BlockedReason') or (key == u'Iteration') or (key == u'Expedite') or (key == u'Build') or (key == u'FormattedID'))}
            #ts_data = self.data['ts']
            for key in ts_data.iterkeys():
                if ((type(ts_data[key]) is not unicode) and (type(ts_data[key]) is not str) and (type(ts_data[key]) is not int) and (type(ts_data[key]) is not bool) and (type(ts_data[key]) is not float)):
                    ts_data[key]=ts_data[key]._ref            
            ts = self.rally.post('TestSet', ts_data)  
            self.logger.debug("Test Set %s is updated" % ts.FormattedID)        
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            self.logger.error('ERROR: %s \n' % details)
            sys.exit(1)
        #print "Test Set %s updated" % ts.FormattedID
        #print "--------------------------------------------------------------------"
        return ts    
    '''