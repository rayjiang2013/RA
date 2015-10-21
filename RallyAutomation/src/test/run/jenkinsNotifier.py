'''
To handle jenkins related functionalities

@author: ljiang
'''
import sys
import logging
import inspect
from copy import deepcopy
from jenkinsapi.build import Build
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.job import Job

class jenkinsNotifier(object):
    '''
    This is the class module to handle jenkins related functionalities
    @summary: This class is used to handle jenkins related functionalities
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

    def getServerInstance(self):
        '''
        @summary: To get the jenkins session instance
        @status: completed
        @raise details: log errors
        @return: return created jenkins session instance
        '''
        try: 
            jenkins_info = deepcopy(self.data['jenkins'])
            server = Jenkins(jenkins_info['url'], username = jenkins_info['username'], password = jenkins_info['password'])
            self.logger.debug("Jenkins instance at %s with version %s is successfully obtained" % (server.baseurl, server.version))
            return server    
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
    
    def getLastBuildInfo(self,server):
        '''
        @summary: To get the latest jenkins build
        @status: completed
        @param server: jenkins session instance
        @raise details: log errors
        @return: return latest jenkins build object and job object
        '''        
        try: 
            job_obj=Job(server.baseurl+"/job/"+self.data['builddf']['Name'],self.data['builddf']['Name'],server)
            last_bd=job_obj.get_last_build_or_none()
            self.logger.debug("The last build at %s is %s" % (server.baseurl, last_bd.name))
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
        return (last_bd,job_obj)        
