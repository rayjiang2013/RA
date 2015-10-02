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

#The bugs https://github.com/RallyTools/RallyRestToolkitForPython/issues/37 and
#https://github.com/RallyTools/RallyRestToolkitForPython/issues/40
#should be fixed according comments from the po. But another bug
#https://github.com/RallyTools/RallyRestToolkitForPython/issues/37
#still exists; so use pyrallei instead
#from pyral import Rally,rallyWorkset

#By using custom package pyrallei as a workaround for the bug:
#https://github.com/RallyTools/RallyRestToolkitForPython/issues/37;
#have to switch to my personal package again for
#https://github.com/jay6413682/RallyRestToolkitForPython/comit
#/7dbec761a924ada0bdfe379b385a2b00e9875b21
from pyrallei import Rally, rallyWorkset

#The main function
def main():
    '''
    This main() function is the start point of execution for the test automation framework.
    It defines the flow of action the test automation framework executes.
    '''
    if __name__ == '__main__':
        #Setup
        try:
            #logConfig("logging.json")
            logger = setup(sys.argv[3])
            #logger = logging.getLogger(__name__)
            logger.propagate = False
            options = [opt for opt in sys.argv[1:] if opt.startswith('--')]

            #apikey can be obtained from https://rally1.rallydev.com/login/
            server, user, password, apikey, workspace, project = rallyWorkset(options)
            logger.debug("Rally project info is as below:\n %s", \
                         " ".join(['|%s|' % opt for opt in \
                        [server, user, password, apikey, workspace, project]]))

            #include apikey=apikey to workaround
            #http://stackoverflow.com/questions/30495164
            #/getting-error-rallyrestapierror-422-not-authorized-to-perform-action-invalid
            #and http://stackoverflow.com/questions/30492008
            #/net-rally-restapi-error-not-authorized-to-perform-action-invalid-key-when-cr
            rally = Rally(server, user, password, apikey=apikey, \
                          workspace=workspace, project=project)

            rally.enableLogging('rally.example.log', attrget=True, append=True)
            # Read other configuration parameters from the extra.json
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
            if to_obj.sanityCheck(data['ts']['FormattedID'], *constants.CHECK_IP):
                to_obj.getLastBuildInfoFromJenkins()
                to_obj.updateBuildInfo()
                to_obj.getLatestBuild()
                ts_ut = to_obj.copyTS()
                (verd, newdt) = to_obj.runTO(ts_ut)
                test_results = to_obj.runTS(verd, newdt)
                report = report_obj.genReport(test_results, constants.FROM_TR)
                notification_obj.sendNotification(report)
        except Exception, details:
            #print details
            logger.error('ERROR: %s \n', details, exc_info=True)
            sys.exit(1)

if __name__ == '__main__':
    main()
    