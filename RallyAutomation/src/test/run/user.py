'''
To interact with Rally users

@author: ljiang
'''
import sys
import logging
import inspect

class user:
    '''
    This is the class module for Rally user
    @summary: This class is used to provide Rally user related functionalities
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

    def getUser(self):
        '''
        @summary: get a Rally user of a specific username
        @status: completed
        @raise details: log errors
        @return: return Rally user object
        '''
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
            self.logger.debug("User obtained, Name: %s, Content: %s" % (usr.UserName,dic))
            #print "User obtained, Name: %s, Content: " % usr.UserName
            #pprint(dic)
            #print "--------------------------------------------------------------------"
            return usr
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)