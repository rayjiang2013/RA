'''
To connect the framework with mysql api - sqlFunctions

@author: ljiang
'''
import logging
import inspect
import constants
import sys
from sqlFunctions import sql_functions 

class sqlConnector(object):
    '''
    To connect the test automation framework with mysql api - sqlFunctions
    @summary: This class is used to connect the test automation framework with mysql api - sqlFunctions
    @status: under development
    @ivar data: dictionary parsed from extra.json
    @ivar rally: Rally session object
    @ivar logger: the logger for testObject
    '''
    def __init__(self,config_name,config_data):

        self.config_name=config_name
        self.config_data=config_data
        #setup("logging.json")
        #logger.debug("testObject is initiated successfully")
        self.logger = logging.getLogger(__name__)
        self.logger.propagate=False

    #formulate the test cases like in Rally custom field
    def getTCFromDB(self,tc_name):
        '''
        @summary: To get the test cases data from database and formulate similar string
            like in Rally so the test framework can process it
        @status: completed
        @type tc_name: string
        @param tc_name: the name of the test case
        @raise details: log errors
        @return: return the reformulated test case data
        '''
        try:
            sql_obj=sql_functions(self.config_name,'sqldb')
            #need implement#
            table_name=str(self.config_data['table'])
            tc_data=sql_obj.create_select(table_name,'*',**{'TestCaseName':tc_name})
            tc_fields_list=['']*constants.NO_TC_FIELDS
            if tc_data[1][0][7]!=None:
                sup_fields=tc_data[1][0][7].split('|')
                for i,j in zip(constants.INDEXES_SUP,xrange(len(sup_fields))):
                    tc_fields_list[i]=str(sup_fields[j])
            if tc_data[1][0][8]!=None:
                exe_fields=tc_data[1][0][8].split('|')
                for i,j in zip(constants.INDEXES_EXE,xrange(len(exe_fields))):
                    tc_fields_list[i]=str(exe_fields[j])
            if tc_data[1][0][9]!=None:
                flc_fields=tc_data[1][0][9].split('|')
                for i,j in zip(constants.INDEXES_FLC,xrange(len(flc_fields))):
                    tc_fields_list[i]=str(flc_fields[j])
            if tc_data[1][0][10]!=None:
                ver_fields=tc_data[1][0][10].split('|')
                for i,j in zip(constants.INDEXES_VER,xrange(len(ver_fields))):
                    tc_fields_list[i]=str(ver_fields[j])
            if tc_data[1][0][6]!=None:
                clu_fields=tc_data[1][0][6].split('|')
                for i,j in zip(constants.INDEXES_CLU,xrange(len(clu_fields))):
                    tc_fields_list[i]=str(clu_fields[j])
            tc_string='|'.join(tc_fields_list)
        except Exception, details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
        return tc_string