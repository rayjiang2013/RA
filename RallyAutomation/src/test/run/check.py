'''
This class is to provide useful functions for sanity or env check

By Lei J

'''
import logging
import requests
import json
import datetime
import inspect

class check:
    def __init__(self,data,rally):
        '''
        Pass the test related data
        '''
        self.data=data
        self.rally=rally
        #setup("logging.json")
        #logger.debug("testObject is initiated successfully")
        self.logger = logging.getLogger(__name__)
        self.logger.propagate=False   
    
    def checkLic(self,ts_id):
        try:
            s=requests.session()
            license_url=self.data['env']['ControllerURL']+'/contents/read_licenses'
            r_license=s.get(license_url)
            r_license_dict=json.loads(r_license.content)
            if r_license.status_code !=200:
                raise("License check failed: unexpected response code")
            #check if ok equals true and the expiration date has not been reached yet for license.
            if r_license_dict['ok']!=True:
                raise("License check failed: the response is not ok")
            time_now=str(datetime.datetime.now())
            date_now=time_now.split()[0]
            for expiration_date in r_license_dict['resp']['expire_at'].values():
                if expiration_date<date_now:
                    if expiration_date!='0000-00-00':
                        raise("License check failed: license expired")
            #check if ok equals true and the expiration date has not been reached yet for license server
            license_server_url=self.data['env']['ControllerURL']+'/license_servers'
            r_license_server=s.get(license_server_url)
            r_license_server_dict=json.loads(r_license_server.content)
            if r_license_server.status_code !=200:
                raise("License server check failed: unexpected response code")

            if r_license_server_dict['ok']!=True:
                raise("License server check failed: the response is not ok")
            time_now=str(datetime.datetime.now())
            date_now=time_now.split()[0]
            for feature in r_license_server_dict['data'][0]['features']:
                if feature['daysTilExpiry']<=0:
                    raise("License server check failed: license server expired")            
            
            s.close()
            self.logger.debug("The license/license server (%s) is working properly" % (r_license_server_dict['data'][0]['ip']))
            return True
        except Exception,details:

            x=inspect.stack()

            if details.message in ['License check failed: unexpected response code','License check failed: the response is not ok','License check failed: license expired','License server check failed: unexpected response code','License server check failed: the response is not ok','License server check failed: license server expired']:
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                report_data=[]
                report_data.append("Test Report for Test Set %s:\n" % ts_id)                                           
                report_data.append("Test Set ID: %s\nBuild: %s\nVerdict: Blocked\nNotes: %s\nDate: %s\nTester: %s\n" % (ts_id,self.data["ts"]["Build"],details,datetime.datetime.now(),self.data['user']['UserName']))  
                report=self.genReport(report_data,constants.FROM_EXCEPTION)
                self.sendNotification(report)    
                sys.exit(1)  
            elif 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)            
            