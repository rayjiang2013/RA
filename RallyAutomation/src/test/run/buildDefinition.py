'''
To interact with Rally builddefinition

@author: ljiang
'''
import sys
import logging
import inspect

class buildDefinition(object):
    '''
    Provide Rally builddefinition related functionalities
    @summary: This class is used to provide Rally builddefinition related functionalities
    @status: under development
    @ivar data: dictionary parsed from extra.json
    @ivar rally: Rally session object
    @ivar logger: the logger for testObject
    '''
    def __init__(self, rally,data):
        '''
        Constructor of Rally build definition
        '''
        self.data=data
        self.rally=rally
        self.logger = logging.getLogger(__name__)
        self.logger.propagate=False

    #get a builddefinition specified by name
    def getBuildDefinitionByName(self):
        '''
        @summary: get a builddefinition identified by the name of builddefinition
        @status: completed
        @raise details: log errors
        @return: return Rally builddefinition object
        '''
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
        '''
        @summary: create a builddefinition
        @status: completed
        @raise details: log errors
        @return: return the builddefinition created
        '''
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
        '''
        @summary: get all the builddefinitions in Rally
        @status: completed
        @raise details: log errors
        @return: return a list of Rally builddefinitions
        '''
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
