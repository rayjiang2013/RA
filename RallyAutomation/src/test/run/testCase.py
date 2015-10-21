'''
To interact with Rally test case

@author: ljiang
'''
import sys
import logging
import inspect

class testCase:
    '''
    This is the class module for Rally test case
    @summary: This class is used to provide Rally test case related functionalities
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

    #Show a TestCase identified by the FormattedID value
    def getTCByID(self):
        '''
        @summary: get a test case identified by the formattedid
        @status: completed
        @raise details: log errors
        @return: return Rally test case object
        '''
        try:
            query_criteria = 'FormattedID = "%s"' % str(self.data['tc']['FormattedID'])
            response = self.rally.get('TestCase', fetch=True, query=query_criteria)
            dic={}
            for tc in response:
                for key in dir(tc):
                    if not key.endswith("__"):
                        dic[key]=getattr(tc,key)
                    #print key,getattr(tc,key)
                break        
            #print "Test case obtained, ObjectID: %s  FormattedID: %s  Content: " % (tc.oid,tc.FormattedID)
            #pprint(dic)
            self.logger.debug("Test case obtained, ObjectID: %s  FormattedID: %s  Content: %s" % (tc.oid,tc.FormattedID,dic))
            return tc
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            #sys.exit(1)
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)

    #get all test cases
    def getAllTCs(self,query_criteria):
        '''
        @summary: get all the test cases under a test case in Rally
        @type query_criteria: string or list
        @param query_criteria: the query(s)
        @status: completed
        @raise details: log errors
        @return: return a list of test cases
        '''
        try:
            #query_criteria = 'BuildDefinition = "%s"' % (str(self.data['build']['BuildDefinition']))
            response = self.rally.get("TestCase", fetch=True,query=query_criteria)
            tcs=[]
            for tc in response:
                tcs.append(tc)                    
                self.logger.debug("Test case obtained, ObjectID: %s  Test Case name: %s \n" % (tc.oid,tc.Name))
            return tcs
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            #sys.exit(1)
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)    

    #Create test case
    def createTC(self):
        '''
        @summary: create a test case
        @status: completed
        @raise details: log errors
        @return: return the test case created
        '''
        tc_data = {key: value for key, value in self.data['tc'].items() if key != u'FormattedID'} #Create a test case with all fields of data['tc'] except the key value pair of 'FormattedID'
        try:
            tc = self.rally.put('TestCase', tc_data)
            self.logger.debug("Test case created, ObjectID: %s  FormattedID: %s" % (tc.oid, tc.FormattedID))
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
        #print "Test case created, ObjectID: %s  FormattedID: %s" % (tc.oid, tc.FormattedID)
        return tc  
        
    #Update test case
    def updateTC(self):
        '''
        @summary: update a test case
        @status: completed
        @raise details: log errors
        @return: return the test case updated
        '''
        tc_data = self.data['tc']
        try: 
            tc = self.rally.post('TestCase', tc_data)
            self.logger.debug("Test Case %s updated" % tc.FormattedID)          
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
        #print "Test Case %s updated" % tc.FormattedID
        return tc
    
    #Delete test case
    def delTC(self):
        '''
        @summary: delete a test case
        @status: completed
        @raise details: log errors
        @return: return None
        '''
        try: 
            delete_success=self.rally.delete('TestCase', self.data['tc']['FormattedID'])
            if delete_success == True:
                #print "Test case deleted, FormattedID: %s" % self.data['tc']['FormattedID']
                self.logger.debug("Test case deleted, FormattedID: %s" % self.data['tc']['FormattedID']) 
        except Exception, details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s %s %s does not exist\n' % (Exception,details,self.data['tc']['FormattedID']), exc_info=True)
                sys.exit(1)
