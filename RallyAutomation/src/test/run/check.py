'''
This module is to provide useful functions for sanity or env check

@author: ljiang
'''
# pylint: disable=fixme, relative-import
# pylint: disable=fixme, broad-except
# pylint: disable=fixme, invalid-name
import sys
import os
sys.path.append(os.path.dirname(__file__))
import logging
import requests
import json
import datetime
import inspect
import constants
import platform
import subprocess
from copy import copy
from notification import Notification
from reporting import Reporting

class check:
    '''
    To provide funcs for sanity or env check
    @summary: This class is used to provide high level actions the framework can perform
    @status: under development
    @ivar data: dictionary parsed from extra.json
    @ivar rally: Rally session object
    @ivar logger: the logger for testObject
    '''
    def __init__(self, data, rally):
        '''
        Pass the test related data
        '''
        self.data = data
        self.rally = rally
        #setup("logging.json")
        #logger.debug("testObject is initiated successfully")
        self.logger = logging.getLogger(__name__)
        self.logger.propagate = False

    def checkLic(self, ts_id):
        '''
        @summary: To check if the license/license server is working properly
        @status: under development
        @type ts_id: string
        @param ts_id: id of test set
        @raise details: handle license related exceptions - 'License check failed: unexpected response code',
            'License check failed: the response is not ok',
            'License check failed: license expired',
            'License server check failed: unexpected response code',
            'License server check failed: the response is not ok',
            'License server check failed: license server expired',
            and send reports if certain exception is caught
        @return: return True if all the steps pass
        '''
        try:
            s = requests.session()
            license_url = self.data['env']['ControllerURL'] + '/contents/read_licenses'
            r_license=s.get(license_url)
            r_license_dict = json.loads(r_license.content)
            if r_license.status_code != 200:
                raise Exception("License check failed: unexpected response code")
            #check if ok equals true and the expiration date has not been reached yet for license.
            if r_license_dict['ok'] != True:
                raise Exception("License check failed: the response is not ok")
            time_now = str(datetime.datetime.now())
            date_now = time_now.split()[0]
            for expiration_date in r_license_dict['resp']['expire_at'].values():
                if expiration_date < date_now:
                    if expiration_date != '0000-00-00':
                        raise Exception("License check failed: license expired")
            #check if ok equals true and
            #the expiration date has not been reached yet for license server
            license_server_url = self.data['env']['ControllerURL'] + '/license_servers'
            r_license_server = s.get(license_server_url)
            r_license_server_dict = json.loads(r_license_server.content)
            if r_license_server.status_code != 200:
                raise Exception("License server check failed: unexpected response code")
            if r_license_server_dict['ok'] != True:
                raise Exception("License server check failed: the response is not ok")
            time_now = str(datetime.datetime.now())
            date_now = time_now.split()[0]
            for feature in r_license_server_dict['data'][0]['features']:
                if feature['daysTilExpiry'] <= 0:
                    raise Exception("License server check failed: license server expired")
            s.close()
            self.logger.debug("The license/license server (%s) is working properly",
                              (r_license_server_dict['data'][0]['ip']))
            return True
        except Exception,details:
            inspt = inspect.stack()
            notification_obj = Notification(self.rally, self.data)
            report_obj = Reporting(self.rally, self.data)
            if details.message in ['License check failed: unexpected response code',
                                   'License check failed: the response is not ok',
                                   'License check failed: license expired',
                                   'License server check failed: unexpected response code',
                                   'License server check failed: the response is not ok',
                                   'License server check failed: license server expired']:
                self.logger.error('ERROR: %s \n', details, exc_info=True)
                report_data=[]
                report_data.append("Test Report for Test Set %s:\n" % ts_id)
                report_data.append("Test Set ID: %s\nBuild: %s\nVerdict: "
                                    "Blocked\nNotes: %s\nDate: %s\nTester: %s\n" %
                                   (ts_id, self.data["ts"]["Build"],
                                    details, datetime.datetime.now(),
                                    self.data['user']['UserName']))
                report = report_obj.genReport(report_data, constants.FROM_EXCEPTION)
                notification_obj.sendNotification(report)
                sys.exit(1)
            elif 'test_' in inspt[1][3] or 'test_' in inspt[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n', details, exc_info=True)
                sys.exit(1)

    def ping(self, ts_id, *args):
        '''
        @summary: To ping all CHECK_IP defined in constants.py
        @status: under development
        @type ts_id: string
        @param ts_id: id of test set
        @param args: a list of ip/hosts to check against
        @raise details: handle ping related exceptions - "ping: cannot resolve nonexist: Unknown host",
            "Request timeout", and send reports if certain exception is caught
        @return: return error message if there is any otherwise return empty string
        '''
        try:
            plat_ident = platform.system()
            if plat_ident.startswith('CYGWIN'):
                plat_ident = 'Cygwin'
            for target in args:
                vector = copy(constants.PING_COMMAND[plat_ident])
                vector.append(target)
                p = subprocess.Popen(vector, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, errors = p.communicate()
                if errors == 'ping: cannot resolve nonexist: Unknown host\n':
                    raise Exception("ping: cannot resolve nonexist: Unknown host")
                if 'Request timeout for icmp_seq 0' in output:
                    raise Exception('Request timeout for %s' % target)
            return errors
        except Exception, details:
            inspt = inspect.stack()
            notification_obj = Notification(self.rally, self.data)
            report_obj = Reporting(self.rally, self.data)
            if 'test_' in inspt[1][3] or 'test_' in inspt[2][3]:
                raise
            elif details.message in ['ping: cannot resolve nonexist: Unknown host',
                                   'Request timeout for %s' % target]:
                self.logger.error('ERROR: %s \n', details, exc_info=True)
                report_data=[]
                report_data.append("Test Report for Test Set %s:\n" % ts_id)
                report_data.append("Test Set ID: %s\nBuild: %s\n"
                                   "Verdict: Blocked\nNotes: %s\nDate: %s\nTester: %s\n" %
                                   (ts_id, self.data["ts"]["Build"],
                                    details, datetime.datetime.now(),
                                    self.data['user']['UserName']))
                report = report_obj.genReport(report_data, constants.FROM_EXCEPTION)
                notification_obj.sendNotification(report)
                sys.exit(1)
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n', details, exc_info=True)
                sys.exit(1)
