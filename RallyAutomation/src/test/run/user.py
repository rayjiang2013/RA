'''
Created on Nov 11, 2014

@author: ljiang
'''
import sys
from pprint import pprint

import logging
from logging import config

logger = logging.getLogger(__name__)

class user:
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
    def getUser(self):
        try:
            query_criteria = 'UserName = "%s"' % str(self.data['user']['UserName'])
            response = self.rally.get('User', fetch=True, query=query_criteria)
            dic={}
            for usr in response:
                for key in dir(usr):
                    if not key.endswith("__"):
                        dic[key]=getattr(usr,key)
                    #print key,getattr(usr,key)
                break        
            print "User obtained, Name: %s, Content: " % usr.UserName
            pprint(dic)
            print "--------------------------------------------------------------------"
            return usr
        except Exception, details:
            sys.stderr.write('ERROR: %s \n' % details)
            sys.exit(1)