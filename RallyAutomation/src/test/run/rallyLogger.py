'''
Created on Nov 19, 2014

@author: ljiang
'''
import logging.config
import json
import sys
import inspect

def setup(log_config):
    '''To setup logging configuration'''
    try:
        with open(log_config, 'rt') as f:
            config = json.load(f)
            logging.config.dictConfig(config)
            logger = logging.getLogger(__name__)
            logger.propagate=False
            logger.debug("The logging configuration is successfully loaded")
    except Exception,details:
        #x=inspect.stack()
        if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
            raise
        else:
            print Exception,details
            logger.error('ERROR: %s \n' % details,exc_info=True)
            sys.exit(1)
    return logger
