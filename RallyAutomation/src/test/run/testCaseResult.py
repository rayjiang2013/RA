'''
Created on Nov 12, 2014

@author: ljiang
'''
import sys
from pprint import pprint

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
        
    #Create test case
    def createTCResult(self):
        try:
            tr = self.rally.put('TestCaseResult', self.data['tcresult'])
        except Exception, details:
            sys.stderr.write('ERROR: %s \n' % details)
            sys.exit(1)
        print "Test Case %s updated; Test result oid %s is created" % (tr.TestCase.FormattedID,tr.oid)     
        return tr  