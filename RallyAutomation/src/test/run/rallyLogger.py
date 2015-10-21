'''
To setup logging configuration

@author: ljiang
'''
# pylint: disable=fixme, broad-except
import logging.config
import json
import sys
import inspect

def setup(log_config):
    '''
    @summary: To setup logging configuration
    @status: completed
    @type log_config: string
    @param log_config: name of the log config file
    @raise details: log errors
    @return: return the logger object
    '''
    try:
        with open(log_config, 'rt') as f:
            config = json.load(f)
            logging.config.dictConfig(config)
            logger = logging.getLogger(__name__)
            logger.propagate = False
            logger.debug("The logging configuration is successfully loaded")
    except Exception, details:
        #x=inspect.stack()
        if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
            raise
        else:
            #print Exception,details
            logger.error('ERROR: %s \n', details, exc_info=True)
            sys.exit(1)
    return logger
