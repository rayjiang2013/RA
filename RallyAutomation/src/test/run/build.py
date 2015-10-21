'''
To interact with Rally builds

@author: ljiang
'''
import sys
import logging
import inspect

class build(object):
    '''
    Provide Rally build related functionalities
    @summary: This class is used to provide Rally build related functionalities
    @status: under development
    @ivar data: dictionary parsed from extra.json
    @ivar rally: Rally session object
    @ivar logger: the logger for testObject
    '''
    def __init__(self, rally,data):
        '''
        Constructor of Rally test case
        '''
        self.data=data
        self.rally=rally
        self.logger = logging.getLogger(__name__)
        self.logger.propagate=False

    #get a build identified by the build number and BuildDefinition ref
    def getBuild(self):
        '''
        @summary: get a build identified by the build number and BuildDefinition ref
        @status: completed
        @raise details: log errors
        @return: return Rally build object
        '''
        try:
            query_criteria = '(Number = "%s") and (BuildDefinition = "%s")' % (str(self.data['ts']['Build']),str(self.data['build']['BuildDefinition']))
            response = self.rally.get('Build', fetch=True, query=query_criteria)
            dic={}
            for build in response:
                for key in dir(build):
                    if not key.endswith("__"):
                        dic[key]=getattr(build,key)
                    #print key,getattr(build,key)
                break
            self.logger.debug("Build obtained, ObjectID: %s  Build Number: %s  Content: %s" % (build.oid,build.Number,dic))
            return build
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

    #get all builds
    def getAllBuilds(self):
        '''
        @summary: get all the builds in Rally
        @status: completed
        @raise details: log errors
        @return: return a list of Rally builds
        '''
        try:
            #query_criteria = 'BuildDefinition = "%s"' % (str(self.data['build']['BuildDefinition']))
            response = self.rally.get('Build', fetch=True)#query=query_criteria)
            builds=[]
            for build in response:
                builds.append(build)                    
                self.logger.debug("Build obtained, ObjectID: %s  Build Number: %s\n" % (build.oid,build.Number))
            return builds
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

    #Create build
    def createBuild(self):
        '''
        @summary: create a build
        @status: completed
        @raise details: log errors
        @return: return the build created
        '''
        bd_data = {key: value for key, value in self.data['build'].items()}
        try:
            bd = self.rally.put('Build', bd_data)
            self.logger.debug("Build created, ObjectID: %s, Number: %s" % (bd.oid, bd.Number))
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
        return bd
