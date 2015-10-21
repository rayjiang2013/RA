'''
To send email notification

@author: ljiang
'''
import sys
import os.path
sys.path.append(os.path.dirname(__file__))
import logging
from smtplib import SMTP, SMTPException
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import inspect

class Notification(object):
    '''
    Include functions to send email notification
    @summary: This class is used to handle jenkins related functionalities
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

    #Send email notification; two ways -
    #1.http://z3ugma.github.io/blog/2014/01/26/getting-python-working-on-microsoft-exchange/
    #not working, hold for now
    #2. http://www.tutorialspoint.com/python/python_sending_email.htm
    # Also, the current smtp server of spirent
    # does not allow sending email to email address outside the spirent domain.
    def sendNotification(self,fname):
        '''
        @summary: To send notification
        @status: completed
        @type fname: string
        @param fname: the name of the report file
        @raise details: log errors
        @return: return None
        '''
        try:
            #Create the email.
            msg = MIMEMultipart()
            msg["Subject"] = str(self.data['email']['EMAIL_SUBJECT']) #EMAIL_SUBJECT
            msg["From"] =  str(self.data['email']['EMAIL_FROM']) #EMAIL_FROM
            msg["To"] =  str(",".join(self.data['email']['EMAIL_RECEIVER']))
            #body = MIMEMultipart('alternative')
            #body.attach(MIMEText("test", TEXT_SUBTYPE))
            #Attach the message
            #msg.attach(body)
            #Attach a text file
            msg.attach(MIMEText(file(fname).read()))
            #smtpObj = SMTP(GMAIL_SMTP, GMAIL_SMTP_PORT)
            smtpObj = SMTP(str(self.data['email']['EMAIL_SMTP']), \
                           self.data['email']['EMAIL_SMTP_PORT'])
            #Identify yourself to GMAIL ESMTP server.
            smtpObj.ehlo()
            #Put SMTP connection in TLS mode and call ehlo again.
            #smtpObj.starttls()
            #smtpObj.ehlo()
            #Login to service
            #user=EMAIL_FROM, password=EMAIL_PASSWD
            #Actually the spirent smtp server does not allow authentication, so no login is needed
            #smtpObj.login(None,None)
            #Send email
            #smtpObj.sendmail(EMAIL_FROM, EMAIL_RECEIVER, msg.as_string())
            smtpObj.sendmail(msg["From"], msg["To"].split(','), msg.as_string())
            #close connection and session.
            smtpObj.quit()
            #print "The report is successfully sent"
            #print "--------------------------------------------------------------------"
            self.logger.info("The report is successfully sent")
        except SMTPException as error:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error("Error: unable to send email :  {err}".format(err=error), exc_info=True)
                sys.exit(1)
