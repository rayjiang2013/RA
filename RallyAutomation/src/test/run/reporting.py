'''
Created on Sep 30, 2015

To handle reporting

@author: ljiang
'''
import sys
import os.path
sys.path.append(os.path.dirname(__file__))
import logging
from helper import helper
import datetime
import inspect

class Reporting(object):
    '''
    Include functions to send notification
    '''
    def __init__(self, rally, data):
        '''
        Constructor of testObject
        '''
        self.data = data
        self.rally = rally
        self.logger = logging.getLogger(__name__)
        self.logger.propagate = False
        self.helper_obj = helper(rally, data)

    #Generate report
    def genReport(self,trs,from_rally_or_not):
        '''
        To generate the report file
        '''
        filename="Report-%s.log" % datetime.datetime.now()
        try:
            with open(filename,"ab+") as f:
                i=0
                if from_rally_or_not==1:
                    for tr in trs:
                        if i == 0:
                            f.write("Test Report for Test Set %s:\n" % tr.TestSet.FormattedID)
                            i+=1
                        f.write("Test Case ID: %s\nBuild: %s\nVerdict: %s\nDate: %s\nTester: %s\n" %
                        (tr.TestCase.FormattedID,tr.Build,tr.Verdict,tr.Date,tr.Tester.UserName))
                elif from_rally_or_not==0:
                    for line in trs:
                        f.write(line)
            self.logger.info('Report %s is successfully generated', filename)
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n', details, exc_info=True)
                sys.exit(1)
        #print "Report %s is successfully generated" % filename
        #print "--------------------------------------------------------------------"
        return filename
