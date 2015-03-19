'''
Created on Mar 16, 2015

@author: ljiang
'''
import sys
#from pprint import pprint

import logging
#from logging import config
import inspect
from copy import deepcopy
from jenkinsapi.build import Build
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.job import Job

class jenkinsNotifier(object):
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

    def getServerInstance(self):
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
