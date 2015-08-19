'''
To connect the framework with mysql api - sqlFunctions
'''
import logging
import inspect
from sqlFunctions import sql_functions 

class sqlConnector(object):
    '''
    classdocs
    '''
    def __init__(self,config_name,config_data):
        '''
        Constructor
        '''
        self.config_name=config_name
        self.config_data=config_data
        #setup("logging.json")
        #logger.debug("testObject is initiated successfully")
        self.logger = logging.getLogger(__name__)
        self.logger.propagate=False

    #formulate the test cases like in Rally custom field
    def getTCsFromDB(self,tc_name):
        try:
            sql_obj=sql_functions(self.config_name,self.config_data.keys()[0])
            #need implement#

        except Exception, details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)    
        return False