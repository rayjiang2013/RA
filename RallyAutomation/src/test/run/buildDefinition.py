'''
Created on Jan 30, 2015

@author: ljiang
'''
import sys
#from pprint import pprint

import logging
#from logging import config
import inspect

class buildDefinition(object):
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

    
    #get a build identified by the build number and BuildDefinition ref
    def getBuildDefinitionByName(self):
        try:
            query_criteria = 'Name = "%s"' % str(self.data['builddf']['Name'])
            response = self.rally.get('BuildDefinition', fetch=True, query=query_criteria)
            
            dic={}
            
            for builddf in response:
                for key in dir(builddf):
                    if not key.endswith("__"):
                        dic[key]=getattr(builddf,key)
                    #print key,getattr(builddf,key)
                break        
            #print "Test case obtained, ObjectID: %s  FormattedID: %s  Content: " % (tc.oid,tc.FormattedID)
            #pprint(dic)
            
            self.logger.debug("BuildDefinition obtained, ObjectID: %s  Build Number: %s  Content: %s" % (builddf.oid,builddf.Name,dic))
            return builddf
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
         
    
    #Create build definition
    def createBuildDefinition(self):
        bddf_data = {key: value for key, value in self.data['builddf'].items()}
        try:
            bddf = self.rally.put('BuildDefinition', bddf_data)
            self.logger.debug("Build created, ObjectID: %s, Name: %s" % (bddf.oid, bddf.Name))
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
           
        return bddf  
    
    
    #get all build definitions 
    def getAllBuildDefinitions(self):
        try:
            #query_criteria = 'BuildDefinition = "%s"' % (str(self.data['build']['BuildDefinition']))
            response = self.rally.get('BuildDefinition', fetch=True)#query=query_criteria)
            
            builddfs=[]
            
            for builddf in response:
                builddfs.append(builddf)                    
                self.logger.debug("Build definition obtained, ObjectID: %s  Build definition name: %s \n" % (builddf.oid,builddf.Name))
            return builddfs
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

    '''    
    #Update test case
    def updateTC(self):
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
        try: 
            delete_success=self.rally.delete('TestCase', self.data['tc']['FormattedID'])
            if delete_success == True:
                #print "Test case deleted, FormattedID: %s" % self.data['tc']['FormattedID']
                self.logger.debug("Test case deleted, FormattedID: %s" % self.data['tc']['FormattedID']) 
        except Exception, details:
            #sys.stderr.write('ERROR: %s %s %s does not exist\n' % (Exception,details,self.data['tc']['FormattedID']))
            #sys.exit(1)
            
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s %s %s does not exist\n' % (Exception,details,self.data['tc']['FormattedID']), exc_info=True)
                sys.exit(1)
    '''
