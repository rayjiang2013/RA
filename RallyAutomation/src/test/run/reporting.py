'''
To handle reporting

@author: ljiang
'''
import sys
import os.path
sys.path.append(os.path.dirname(__file__))
import logging
import datetime
import inspect

class Reporting(object):
    '''
    Include functions to generate reports
    @summary: This class is used to generate reports
    @status: under development
    @ivar data: dictionary parsed from extra.json
    @ivar rally: Rally session object
    @ivar logger: the logger for testObject
    '''
    def __init__(self, rally, data):
        self.data = data
        self.rally = rally
        self.logger = logging.getLogger(__name__)
        self.logger.propagate = False

    #Generate report
    def genReport(self,trs,from_rally_or_not):
        '''
        @summary: To generate the report file
        @status: completed
        @type trs: list
        @param trs: list of Rally test case result objects if tests finished and are updated in Rally
            or a list report lines if the report comes from the exception raised by sanity check
        @type from_rally_or_not: integer
        @param from_rally_or_not: 1 menas Rally test case results, 0 means raised from sanity check
        @raise details: log errors
        @return: return name of the report file
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
