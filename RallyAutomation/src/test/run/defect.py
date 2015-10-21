'''
To interact with Rally defect

@author: ljiang
'''

import sys
import logging
import inspect

class defect:
    '''
    This is the class module for test case    
    @summary: This class is used to provide Rally defect related functionalities
    @status: under development
    @ivar data: dictionary parsed from extra.json
    @ivar rally: Rally session object
    @ivar logger: the logger for testObject
    '''
    def __init__(self, rally,data):
        '''
        pass data to defect object
        '''
        self.data=data
        self.rally=rally
        self.logger = logging.getLogger(__name__)
        self.logger.propagate=False

    #Create defect
    def createDF(self):
        '''
        @summary: create a defect
        @status: completed
        @raise details: log errors
        @return: return the defect created
        '''
        try:
            df_data = {key: value for key, value in self.data['df'].items() if (key != u'FormattedID')}
            df = self.rally.put('Defect', df_data)
            self.logger.debug("Defect created, ObjectID: %s  FormattedID: %s" % (df.oid, df.FormattedID))      
        except Exception, details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
        return df  

    #Get a defect identified by the FormattedID value
    def getDFByID(self):
        '''
        @summary: get a defect identified by the formattedid
        @status: completed
        @raise details: log errors
        @return: return Rally defect object and a dictionary of the defect data
        '''
        try:            
            query_criteria = 'FormattedID = "%s"' % str(self.data['df']['FormattedID'])
            response = self.rally.get('Defect', fetch=True, query=query_criteria)
            dic={}
            for df in response:
                for key in dir(df):
                    if not key.endswith("__"):
                        dic[key]=getattr(df,key)
                    #print key,getattr(ts,key)
                break
            self.logger.debug("Defect obtained, ObjectID: %s, FormattedID: %s, Content: %s" % (df.oid,df.FormattedID,dic))
            return (df,dic)
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)

    #Fetch all the defects of specific test case            
    def allDFofTC(self,tc):
        '''
        @summary: get all the defects under a test case in Rally
        @status: completed
        @raise details: log errors
        @return: return a list of Rally defects
        '''
        try:
            lst=[]
            #ts_obj=testSet(self.rally,self.data)
            #ts=ts_obj.getTSByID()
            query_criteria = 'TestCase = "%s"' % str(tc._ref)
            response = self.rally.get('Defect', fetch=True, query=query_criteria)
            for df in response:
                lst.append(df)
                #print "Test case obtained, ObjectID: %s  FormattedID: %s" % (tc.oid,tc.FormattedID)
                self.logger.debug("Defect obtained, ObjectID: %s, Formatted ID: %s, test case id: %s" % (df.oid,df.FormattedID,tc.FormattedID))
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
            
    #Update defect
    def updateDF(self):
        '''
        @summary: update a defect
        @status: completed
        @raise details: log errors
        @return: return the defect updated
        '''
        df_data = self.data['df']
        try: 
            df = self.rally.post('Defect', df_data)
            self.logger.debug("Defect %s updated" % df.FormattedID)          
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
        return df
    
    #Delete defect
    def delDF(self):
        '''
        @summary: delete a defect
        @status: completed
        @raise details: log errors
        @return: return True if the defect is deleted successful or False if failed
        '''
        df_id = self.data['df']['FormattedID']
        try: 
            delete_success_or_not = self.rally.delete('Defect', df_id)
            self.logger.debug("Defect %s deleted" % self.data['df']['FormattedID'])          
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
        #print "Test Case %s updated" % tc.FormattedID
        return delete_success_or_not        