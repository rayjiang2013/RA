'''
Created on Nov 12, 2014

@author: ljiang
'''
import sys
#from pprint import pprint

import logging
#from logging import config



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
            self.logger.error('ERROR: %s \n' % details,exc_info=True)
            sys.exit(1)
        #print "Test Case %s updated; Test result oid %s is created" % (tr.TestCase.FormattedID,tr.oid)     
        return tr  