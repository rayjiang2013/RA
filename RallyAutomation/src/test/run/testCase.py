'''
Created on Nov 5, 2014

@author: ljiang
'''
import sys
from pprint import pprint

import logging
from logging import config

logger = logging.getLogger(__name__)

class testCase:
    '''
    This is the class module for test case    
    '''
    def __init__(self, rally,data):
        '''
        Constructor
        '''
        self.data=data
        self.rally=rally
    
    #Show a TestCase identified by the FormattedID value
    def getTCByID(self):
        try:
            query_criteria = 'FormattedID = "%s"' % str(self.data['tc']['FormattedID'])
            response = self.rally.get('TestCase', fetch=True, query=query_criteria)
            dic={}
            for tc in response:
                for key in dir(tc):
                    if not key.endswith("__"):
                        dic[key]=getattr(tc,key)
                    print key,getattr(tc,key)
                break        
            #print "Test case obtained, ObjectID: %s  FormattedID: %s  Content: " % (tc.oid,tc.FormattedID)
            #pprint(dic)
            logger.info("Test case obtained, ObjectID: %s  FormattedID: %s  Content: %s" % (tc.oid,tc.FormattedID,dic))
            return tc
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            #sys.exit(1)
            logger.error('ERROR: %s \n' % details, exc_info=True)
            sys.exit(1)
         
    
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
            

    
