'''
To interact with Rally test case result

@author: ljiang
'''
import sys
import logging
import inspect

class testCaseResult(object):
    '''
    This is the class module for test case result
    @summary: This class is used to provide Rally test case result related functionalities
    @status: under development
    @ivar data: dictionary parsed from extra.json
    @ivar rally: Rally session object
    @ivar logger: the logger for testObject  
    '''
    def __init__(self, rally,data):
        self.data=data
        self.rally=rally
        self.logger = logging.getLogger(__name__)
        self.logger.propagate=False
        
    #Create test case result
    def createTCResult(self):
        '''
        @summary: create a test case result
        @status: completed
        @raise details: log errors
        @return: return the object of test case result created
        '''
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
        '''
        @summary: get all the test case results under a test case in Rally
        @status: completed
        @param tc: the object of Rally test case
        @raise details: log errors
        @return: return a list of Rally test case results
        '''
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
        '''
        @summary: delete a test case result
        @status: completed
        @raise details: log errors
        @return: return None
        '''
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
