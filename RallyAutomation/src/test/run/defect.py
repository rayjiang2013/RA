'''
Created on Dec 3, 2014

@author: ljiang
'''
'''
Created on Nov 5, 2014

@author: ljiang
'''
import sys
#from pprint import pprint

import logging
#from logging import config

import inspect

class defect:
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

    #Create defect
    def createDF(self):
        try:
            df_data = {key: value for key, value in self.data['df'].items() if (key != u'FormattedID')}
            #if ts_dic is not None:
                #ts_data = {key: value for key, value in ts_dic.iteritems() if ((key == u'Name') or (key == u'ScheduleState') or (key == u'Project') or (key == u'Description') or (key == u'Owner') or (key == u'Ready') or (key == u'Release') or (key == u'PlanEstimate') or (key == u'Blocked') or (key == u'BlockedReason') or (key == u'Iteration') or (key == u'Expedite') or (key == u'Build'))}
            #else: ts_data = {key: value for key, value in self.data['ts'].iteritems() if ((key == u'Name') or (key == u'ScheduleState') or (key == u'Project') or (key == u'Description') or (key == u'Owner') or (key == u'Ready') or (key == u'Release') or (key == u'PlanEstimate') or (key == u'Blocked') or (key == u'BlockedReason') or (key == u'Iteration') or (key == u'Expedite') or (key == u'Build'))} #Create a test set with all fields of data['ts'] except the key value pair of 'FormattedID' and 'Build'        
            #ts_data['TestCases']=self.data['ts']['__collection_ref_for_TestCases']
            #for key in ts_data.iterkeys():
                #if ((type(ts_data[key]) is not unicode) and (type(ts_data[key]) is not str) and (type(ts_data[key]) is not int) and (type(ts_data[key]) is not bool) and (type(ts_data[key]) is not float)):
                    #ts_data[key]=ts_data[key]._ref
            df = self.rally.put('Defect', df_data)
            #self.data['ts'].update(ts_data)
            #self.data['ts']=ts_data
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

    #Show a TestSet identified by the FormattedID value
    def getDFByID(self):
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
            #print "Test set obtained, ObjectID: %s  FormattedID: %s " % (ts.oid,ts.FormattedID)
            #print "--------------------------------------------------------------------"
            #pprint(dic)
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
            
    #Update defect
    def updateDF(self):
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