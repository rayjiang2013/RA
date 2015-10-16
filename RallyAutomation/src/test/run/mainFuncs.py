'''
Created on Oct 28, 2014

@author: ljiang
'''
# pylint: disable=fixme, relative-import
# pylint: disable=fixme, broad-except
import sys
import os.path
sys.path.append(os.path.dirname(__file__))
import json
from testObject import testObject
from rallyLogger import setup
import constants
from notification import Notification
from reporting import Reporting
#from sqlConnector import sqlConnector

#By using custom package pyrallei as a workaround for the bug:
#https://github.com/jay6413682/RallyRestToolkitForPython/comit
#/7dbec761a924ada0bdfe379b385a2b00e9875b21
#Watch out for https://github.com/RallyTools/RallyRestToolkitForPython/pull/64
#This pull request may be included in next release
#We will be able to use the official pyral package again
from pyrallei import Rally, rallyWorkset
#from pyral import Rally,rallyWorkset

#The main function
def main():
    '''
    @summary: This main() function is the start point of execution
        for the test automation framework.
        It defines the flow of action the test automation framework executes.
    @return: no return
    @status: under development
    @raise details: log any exceptions
    '''
    if __name__ == '__main__':
        #Setup
        try:
            #logConfig("logging.json")
            #:get logger from rallyLogger.setup function
            logger = setup(sys.argv[3])
            #logger = logging.getLogger(__name__)
            # If you attach a handler to a logger and one or more of its ancestors,
            # it may emit the same record multiple times.
            # To prevent logger to pass to the handlers of higher level loggers
            # set the propagate to false
            logger.propagate = False
            #: Get Rally environment info from config.cfg
            options = [opt for opt in sys.argv[1:] if opt.startswith('--')]
            #: apikey can be obtained from https://rally1.rallydev.com/login/
            #: take all options and return useful info to setup connection to Rally
            server, user, password, apikey, workspace, project = rallyWorkset(options)
            # write obtained info to debug log
            logger.debug("Rally project info is as below:\n %s", \
                         " ".join(['|%s|' % opt for opt in \
                        [server, user, password, apikey, workspace, project]]))
            #: setup session with rally
            rally = Rally(server, user, password, apikey=apikey, \
                          workspace=workspace, project=project)

            #rally.enableLogging('rally.example.log', attrget=True, append=True)
            # Read other test related configuration parameters from the extra.json
            with open(sys.argv[2]) as data_file:
                data = json.load(data_file)
                logger.debug("The extra.json configuration file contains \
                            parameters as below: %s", data)
            #Read mysql configuration parameters for mysql.json
            #with open(sys.argv[4]) as mysql_data:
                #mysql_data=json.load(mysql_data)
                #logger.debug("The mysql.json configuration file contains parameters as below: \
                            #%s" % mysql_data)
            #get test case infomation from database
            #sql_obj=sqlConnector(sys.argv[4],mysql_data)
            #tc_string=sql_obj.getTCFromDB('logout')

            to_obj = testObject(rally, data)
            notification_obj = Notification(rally, data)
            report_obj = Reporting(rally, data)
            # do sanity check first, if pass, run the tests
            if to_obj.sanityCheck(data['ts']['FormattedID'], *constants.CHECK_IP):
                to_obj.getLastBuildInfoFromJenkins() # Get latest build from jenkins
                to_obj.updateBuildInfo() # create new build in Rally
                to_obj.getLatestBuild() # Get latest build from rally
                ts_ut = to_obj.copyTS() # copy test set to a new one in Rally
                (verd, newdt) = to_obj.runTO(ts_ut) # run through test set
                test_results = to_obj.runTS(verd, newdt) # update test results in Rally
                report = report_obj.genReport(test_results, constants.FROM_TR) # generate report
                notification_obj.sendNotification(report) # send email notification
        except Exception, details:
            #print details
            logger.error('ERROR: %s \n', details, exc_info=True) # log errors
            sys.exit(1)

# run main function if run started from this module
if __name__ == '__main__':
    main()
    