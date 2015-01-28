'''
Created on Nov 19, 2014

@author: ljiang
'''
import logging
import json
import sys
from logging import config
import inspect


#if not hasattr(logging,'set_up_done'):    
#    logging.set_up_done = False
 
def setup(log_config):
    try:

#        if getattr(logging, 'set_up_done'):
#            return

        with open(log_config, 'rt') as f:
            config = json.load(f)
            logging.config.dictConfig(config)
            logger = logging.getLogger(__name__)
            logger.propagate=False
            logger.debug("The logging configuration is successfully loaded")
    except Exception,details:
        #sys.stderr.write('ERROR: %s \n' % details)
        #x=inspect.stack()
        if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
            raise
        else:
            #print Exception,details
            logger.error('ERROR: %s \n' % details,exc_info=True)
            sys.exit(1)
#    setattr(logging, 'set_up_done', True)
    return logger