'''
Created on Nov 10, 2014

@author: ljiang
'''


#from testSet import *
from smtplib import *
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
#import sys
#from pprint import pprint
#from testSet import *
from testSet import testSet
#from testCase import *
#import testCase
import datetime
#from user import *
from user import user
#from testCaseResult import *
from testCaseResult import testCaseResult
import logging
#import json
#from logging import config
#from rallyLogger import *




class testObject(object):
    '''
    classdocs
    '''


    def __init__(self,rally,data):
        '''
        Constructor
        '''
        self.data=data
        self.rally=rally
        #setup("logging.json")
        #logger.debug("testObject is initiated successfully")
        self.logger = logging.getLogger(__name__)
        self.logger.propagate=False
    '''
    #Update ScheduleState of Test Set 
    def updateSS(self,state):
        try:
            dic={}
            dic['ts']=self.data['ts'].copy()
            dic['ts'].pop('Build',None)
            if state == 0:
                dic['ts']['ScheduleState']="In-Progress"
            if state == 1:        
                dic['ts']['ScheduleState']="Accepted"
            if state == 2:
                dic['ts']['ScheduleState']="Completed"
            ts_obj=testSet(self.rally,dic)
            ts_obj.updateTS()
            #self.data=dic.copy()
            #self.updateTS()
            logger.debug("ScheduleState is successfully updated to %s" % dic['ts']['ScheduleState'])
        except Exception,details:
            logger.error('ERROR: %s \n' % details, exc_info=True)
            sys.exit(1)
    '''
        
    #Main executor & verification      
    def runTO(self):
        '''
        Excute and verification
        '''
        #Update ScheduleState of Test Set 
        '''
        dic={}
        dic['ts']=self.data['ts'].copy()
        dic['ts'].pop('Build',None)
        dic['ts']['ScheduleState']="In-Progress"
        ts_obj=testSet(self.rally,dic)
        ts_obj.updateTS()
        logger.info("ScheduleState is successfully updated")
        '''
        try:
            ts_obj=testSet(self.rally,self.data)
            ts_obj.updateSS(0) 
                    
            verdict=[0,1,1,0]
            self.logger.info("The test run is successfully run")
        except Exception,details:
            self.logger.error("Error: %s\n" % details,exc_info=True)
        return verdict
    
    #Run the test set
    def runTS(self,tc_verds): 
        try:
            ts_obj=testSet(self.rally,self.data)
            ts=ts_obj.getTSByID()
            tcs=ts_obj.allTCofTS(ts)
            #to_obj=testObject(self.rally,self.data)
            #tc_verds=to_obj.runTO() #run the actual tests for AVNext
            ur_obj=user(self.rally,self.data)   
            ur=ur_obj.getUser()
    
            trs=[]
            num_pass=0     
            for tc,verd in zip(tcs,tc_verds):
                dic={}
                if verd == 0:
                    dic['tcresult'] = {'TestCase':tc._ref,'Verdict':u'Fail','Build':self.data["ts"]["Build"],'Date':datetime.datetime.now().isoformat(),'TestSet':ts._ref,'Tester':ur._ref}      
                if verd == 1:
                    dic['tcresult'] = {'TestCase':tc._ref,'Verdict':u'Pass','Build':self.data["ts"]["Build"],'Date':datetime.datetime.now().isoformat(),'TestSet':ts._ref,'Tester':ur._ref}
                    num_pass=num_pass+1
                #try:
                tcr=testCaseResult(self.rally,dic)                
                #tr=self.rally.put('TestCaseResult', dic)
                tr=tcr.createTCResult() 
                trs.append(tr)          
                #except Exception, details:
                    #sys.stderr.write('ERROR: %s \n' % details)
                    #sys.exit(1)
                #print "Test Case %s updated; Test result oid %s is created" % (tc.FormattedID,tr.oid)
            '''
            #Update ScheduleState of Test Set 
            dic={}
            dic['ts']=self.data['ts'].copy()
            dic['ts'].pop('Build',None)        
            if num_pass == len(tc_verds):        
                dic['ts']['ScheduleState']="Accepted"
            else:
                dic['ts']['ScheduleState']="Completed"
            ts_obj_2=testSet(self.rally,dic)
            ts_obj_2.updateTS()
            '''
            if num_pass == len(tc_verds):
                ts_obj.updateSS(1) 
            else:
                ts_obj.updateSS(2)       
            self.logger.info("The test set %s is successfully run on Rally" % ts.FormattedID)     
        except Exception,details:
            self.logger.error("Error: %s\n" % details,exc_info=True)
        return trs
        
    #Generate report
    def genReport(self,trs):
        filename="Report-%s.log" % datetime.datetime.now()
        try:
            with open(filename,"ab+") as f:
                for tr in trs:
                    f.write("Test Report for Test Set %s:\nTest Case ID: %s\nBuild: %s\nVerdict: %s\nDate: %s\nTester: %s\n" % (tr.TestSet.FormattedID,tr.TestCase.FormattedID,tr.Build,tr.Verdict,tr.Date,tr.Tester.UserName))
            self.logger.info('Report %s is successfully generated' % filename)
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            self.logger.error('ERROR: %s \n' % details, exc_info=True)
            sys.exit(1)
        #print "Report %s is successfully generated" % filename   
        #print "--------------------------------------------------------------------"     
        return filename
            
    
    #Send email notification; two ways - 1.http://z3ugma.github.io/blog/2014/01/26/getting-python-working-on-microsoft-exchange/    not working, hold for now
    #2. http://www.tutorialspoint.com/python/python_sending_email.htm
    
    def sendNotification(self,fname):
        try:
            #Create the email.
            msg = MIMEMultipart()
            msg["Subject"] = str(self.data['email']['EMAIL_SUBJECT']) #EMAIL_SUBJECT 
            msg["From"] =  str(self.data['email']['EMAIL_FROM']) #EMAIL_FROM   
            msg["To"] =  str(",".join(self.data['email']['EMAIL_RECEIVER'])) #",".join(EMAIL_RECEIVER)   
            #body = MIMEMultipart('alternative')
            #body.attach(MIMEText("test", TEXT_SUBTYPE))
            #Attach the message
            #msg.attach(body)
            #Attach a text file
            msg.attach(MIMEText(file(fname).read()))  
        
            #smtpObj = SMTP(GMAIL_SMTP, GMAIL_SMTP_PORT)
            smtpObj = SMTP(str(self.data['email']['EMAIL_SMTP']), self.data['email']['EMAIL_SMTP_PORT'])
            #Identify yourself to GMAIL ESMTP server.
            smtpObj.ehlo()
            #Put SMTP connection in TLS mode and call ehlo again.
            #smtpObj.starttls()
            #smtpObj.ehlo()
            #Login to service
            #smtpObj.login(None,None)#user=EMAIL_FROM, password=EMAIL_PASSWD) Actually the spirent smtp server does not allow authentication, so no login is needed
            #Send email
            #smtpObj.sendmail(EMAIL_FROM, EMAIL_RECEIVER, msg.as_string())
            smtpObj.sendmail(msg["From"], msg["To"], msg.as_string())
            #close connection and session.
            smtpObj.quit()
            #print "The report is successfully sent"
            #print "--------------------------------------------------------------------"
            self.logger.info("The report is successfully sent")
        except SMTPException as error:
            #print "Error: unable to send email :  {err}".format(err=error)
            self.logger.error("Error: unable to send email :  {err}".format(err=error),exc_info=True)
        '''
        SERVER = "smtp.gmail.com"
        FROM = "spirenttestsunnyvale@gmail.com"
        TO = ["lei.jiang@spirent.com"] # must be a list
        
        SUBJECT = "Hello!"
        TEXT = "This is a test of emailing through smtp in google."
        
        # Prepare actual message
        message = """From: %s\r\nTo: %s\r\nSubject: %s\r\n\
        
        %s
        """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
       
        # Send the mail
        server = smtplib.SMTP(SERVER,587)
        server.starttls()
        server.ehlo()
        server.login('spirenttestsunnyvale@gmail.com', 'house999')
        server.sendmail(FROM, TO, message)
        server.quit()      
        '''
    '''
    #To log   
    def log(self,log_config):

        with open(log_config, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
        logger.propagate = False
        #root.disabled=True
        #handler = logging.FileHandler('rally-automation-framework-%s.log' % datetime.datetime.now())
        
        
        #logger.addHandler(handler)

        logger.info('Hello baby')
        logger.debug('This is debugging message')
        logger.error('This is an error')
        
        #root.info('Hello baby')
        #root.debug('This is debugging message')
        #root.error('This is an error')
    '''