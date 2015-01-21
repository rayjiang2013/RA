'''
Created on Nov 10, 2014

@author: ljiang
'''


#from testSet import *
from smtplib import *
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import sys
from testSet import testSet
import datetime
from user import user
from testCaseResult import testCaseResult
import logging
from defect import defect
import requests
import ast
from copy import deepcopy

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
        
    #Copy test set
    def copyTS(self):
        try:
            ts_obj=testSet(self.rally,self.data)
            (ts_origin,ts_origin_dic)=ts_obj.getTSByID()
            ts_dst=ts_obj.createTS(ts_origin_dic)
            #ts_new=ts_obj.addTCs(ts_origin,ts_dst)
            ts_new=ts_obj.manualAddTCs(ts_dst)
            self.logger.info("Test set %s is copied to test set %s" % (ts_origin.FormattedID, ts_dst.FormattedID))
            #self.data['ts']={}
            #self.data['ts']['FormattedID']=ts_dst.FormattedID
            #self.logger.info("The test set is successfully copied")
            return ts_new
        except Exception, details:
            self.logger.error('ERROR: %s \n' % details,exc_info=True)
            sys.exit(1)

    #Test execution
    def executor(self,tc):
        try:
            #lst=tc.c_QATCPARAMSSTRING.split('|')
            lst=tc.c_QATCPARAMSTEXT.split('|')
            if lst[0] == "GET":
                r = requests.get(lst[1])                        
            if lst[0] == "POST":
                r = requests.post(lst[1],data=ast.literal_eval(lst[2]))
            if lst[0] == "DELETE":
                r = requests.delete(lst[1])
            if lst[0] == "PUT":
                r = requests.put(lst[1],data=ast.literal_eval(lst[2]))
            
            self.logger.debug("The test case %s for build %s is executed." % (tc.FormattedID,self.data["ts"]["Build"]))       
            return (r,lst) 
        except Exception, details:
            self.logger.error('ERROR: %s \n' % details,exc_info=True)
            sys.exit(1)        
    
    #Test verification:
    def verificator(self,lst,r,verdict,tc):
        try:
            #Verification
            if r.status_code != int(lst[3]):
                verdict.append((0,'Failure: status code unexpected'))    
            else:
                if lst[7]==u"" or lst[5]==u"" or lst[6]==u"":
                    self.logger.debug("As not enough verification information is provided, the test execution for test case %s, build %s is not verified" % (tc.FormattedID,self.data["ts"]["Build"]))
                    verdict.append((1,'Success: status code expected without verification'))
                else:    
                    if lst[7] == "GET":
                        r_ver = requests.get(lst[6])                        
                    if lst[7] == "POST":
                        r_ver = requests.post(lst[6],data=ast.literal_eval(lst[8]))
                    if lst[7] == "DELETE":
                        r_ver = requests.delete(lst[6])
                    if lst[7] == "PUT":
                        r_ver = requests.put(lst[6],data=ast.literal_eval(lst[8]))
                
                    ver_point = ast.literal_eval(lst[5])
                    r_ver_content=ast.literal_eval(r_ver._content)
                    for key in ver_point:                                    
                        if not ((key in r_ver_content) and (ver_point[key]==r_ver_content[key])):
                            verdict.append((0,'Failure: verification failed'))
                            #verified=False
                            self.logger.debug("The test execution for test case %s, build %s is verified to be failed." % (tc.FormattedID,self.data["ts"]["Build"]))   
                            break                  
                    else:                                    
                        #verified=True
                        verdict.append((1,'Success: status code expected and verified'))
                        self.logger.debug("The test execution for test case %s, build %s is verified to be successful." % (tc.FormattedID,self.data["ts"]["Build"]))
        
            return verdict
        except Exception, details:
            self.logger.error('ERROR: %s \n' % details,exc_info=True)
            sys.exit(1)                         
        
    #Cleanup
    def cleaner(self,lst,tc,ts):
        try:
            if lst[10]==u"":
                self.logger.debug("As not enough cleanup information is provided, the test cleanup for test case %s, build %s, test set %s is skipped" % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))
            else: 
                if lst[9] == "GET":
                    r_clr = requests.get(lst[10])                        
                if lst[9] == "POST":
                    r_clr = requests.post(lst[10],data=ast.literal_eval(lst[11]))
                if lst[9] == "DELETE":
                    r_clr = requests.delete(lst[10])
                if lst[9] == "PUT":
                    r_clr = requests.put(lst[10],data=ast.literal_eval(lst[11]))
                
                if int(lst[12])==r_clr.status_code:              
                    self.logger.debug("The test case %s for build %s in test set %s is cleaned up successfully." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))       
                else: 
                    self.logger.debug("The test case %s for build %s in test set %s is failed to clean up." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))       
             
        except Exception, details:
            self.logger.error('ERROR: %s \n' % details,exc_info=True)
            sys.exit(1)    
        
    #Main execution wrapper      
    def runTO(self,testset_under_test):
         
        try:
            verdict=[]
            for tc in testset_under_test.TestCases:
                sorted_trs=sorted(tc.Results, key=lambda x: x.Date, reverse=True)
                #Check if the test case is blocked in most recent run with current build. For...else is used(http://psung.blogspot.com/2007/12/for-else-in-python.html)
                for tr in sorted_trs:
                    if self.data['ts']['Build']==tr.Build:
                        if tr.Verdict=='Blocked':                            
                            #dic['tcresult'] = {'TestCase':tc._ref,'Verdict':u'Blocked','Build':self.data["ts"]["Build"],'Date':datetime.datetime.now().isoformat(),'TestSet':testset_under_test._ref}  
                            #update test case result
                            #tcr=testCaseResult(self.rally,dic)                
                            #tr=tcr.createTCResult() 
                            verdict.append((2,'Blocked:the test case is blocked in last test run with same build id %s' % self.data["ts"]["Build"]))
                            self.logger.debug("The test case %s is blocked for build %s, will skip it." % (tc.FormattedID,self.data["ts"]["Build"]))
                            break
                        else:
                            (response,lst_of_par)=self.executor(tc)
                            verdict=self.verificator(lst_of_par, response, verdict, tc)
                            self.cleaner(lst_of_par, tc,testset_under_test)
                            break
                            
                            
                else:
                    (response,lst_of_par)=self.executor(tc)
                    verdict=self.verificator(lst_of_par, response, verdict, tc)
                    self.cleaner(lst_of_par, tc,testset_under_test)
            
            #Update ScheduleState of Test Set 
            new_data=deepcopy(self.data) 
            new_data['ts']['FormattedID']=testset_under_test.FormattedID
            ts_obj=testSet(self.rally,new_data)
            ts_obj.updateSS(0) 
                    
            #verdict=[0,1,1]
            #verdict=[(0,"Failure reason 3"),(1,"Success reason 3"),(0,"Failure reason 4"),(1,"Success reason 4")]
            self.logger.info("The test run is successfully executed on Chasis")
        except Exception,details:
            self.logger.error("Error: %s\n" % details,exc_info=True)
        return (verdict,new_data)
    
    #Run the test set
    def runTS(self,tc_verds,new_data): 
        try:
            ts_obj=testSet(self.rally,new_data)
            ts=ts_obj.getTSByID()[0]
            tcs=ts_obj.allTCofTS(ts)
            #to_obj=testObject(self.rally,self.data)
            #tc_verds=to_obj.runTO() #run the actual tests for AVNext
            ur_obj=user(self.rally,new_data)   
            ur=ur_obj.getUser()
    
            trs=[]
            num_pass=0     
            for tc,verd in zip(tcs,tc_verds):
                dic={}
                if verd[0] == 0:
                    dic['tcresult'] = {'TestCase':tc._ref,'Verdict':u'Fail','Build':new_data["ts"]["Build"],'Date':datetime.datetime.now().isoformat(),'TestSet':ts._ref,'Tester':ur._ref,'Notes':verd[1]}  
                    df_obj=defect(self.rally,dic)   
                    dfs=df_obj.allDFofTC(tc)
                    i=1
                    #if there is no existing defects in the test case, just create one
                    if len(dfs)==0:
                        #if not exist create new issue for the failed test cases
                        create_df={"FoundInBuild": new_data['ts']['Build'],
                                    "Project": ts.Project._ref,
                                    "Owner": ts.Owner._ref,
                                    "ScheduleState":"Defined",
                                    "State":"Submitted",
                                    "Name":"Error found in %s: %s" % (tc.FormattedID,tc.Name),
                                    "TestCase":tc._ref}
                        new_data['df'].update(create_df)
                        df_obj=defect(self.rally,new_data)
                        new_df=df_obj.createDF()
                        
                        #update test case result
                        tcr=testCaseResult(self.rally,dic)                
                        #tr=self.rally.put('TestCaseResult', dic)
                        tr=tcr.createTCResult() 
                        trs.append(tr)  
                            
                        #update defect with link to test case result
                        update_df={'df':None}
                        update_df['df']={"FormattedID":new_df.FormattedID,"TestCaseResult":tr._ref}
                        df_obj=defect(self.rally,update_df)
                        df_obj.updateDF()    
                        self.logger.debug("The defect %s is linked to test case result %s" % (new_df.FormattedID,tr._ref))  
                    for df in dfs:
                        #if not exist create new issue for the failed test cases
                        if (not hasattr(df.TestCaseResult,'Notes')) or (df.TestCaseResult.Notes != dic['tcresult']['Notes']):
                            if i==len(dfs):

                                create_df={"FoundInBuild": new_data['ts']['Build'],
                                            "Project": ts.Project._ref,
                                            "Owner": ts.Owner._ref,
                                            "ScheduleState":"Defined",
                                            "State":"Submitted",
                                            "Name":"Error found in %s: %s" % (tc.FormattedID,tc.Name),
                                            "TestCase":tc._ref}
                                new_data['df'].update(create_df)
                                df_obj=defect(self.rally,new_data)
                                new_df=df_obj.createDF()
                                
                                #update test case result
                                tcr=testCaseResult(self.rally,dic)                
                                #tr=self.rally.put('TestCaseResult', dic)
                                tr=tcr.createTCResult() 
                                trs.append(tr)  
                                
                                #update defect with link to test case result
                                update_df={'df':None}
                                update_df['df']={"FormattedID":new_df.FormattedID,"TestCaseResult":tr._ref}
                                df_obj=defect(self.rally,update_df)
                                df_obj.updateDF()    
                                self.logger.debug("The defect %s is linked to test case result %s" % (new_df.FormattedID,tr._ref))         
                            i+=1                                
                            continue        
                        #if exist
                        else:
                            #check if the defect is marked as fixed or not
                            if df.State == "Fixed":
                                update_df={'df':None}
                                #reopen the defect, make notes about the build, env and steps. Assign to someone
                                update_df['df']={"FormattedID":df.FormattedID,"State":"Open","Owner":getattr(df.Owner,'_ref',None),"Notes":df.Notes+"<br>The defect is reproduced in build %s, test set %s, test case %s.<br />" % (new_data['ts']['Build'],ts.FormattedID,tc.FormattedID)}        
                                self.logger.debug("The defect %s is reproduced in build %s, test set %s, test case %s. Will re-open and update it with repro info" % (df.FormattedID,new_data['ts']['Build'],ts.FormattedID,tc.FormattedID))                      
                            else: #inserting notes. 
                                update_df={'df':None}
                                #print df.Notes
                                update_df['df']= {"FormattedID":df.FormattedID,"Notes":df.Notes+"The defect is reproduced in build %s, test set %s, test case %s.<br />" % (new_data['ts']['Build'],ts.FormattedID,tc.FormattedID)}
                                self.logger.debug("The defect %s is reproduced in build %s, test set %s, test case %s. Will update it with repro info" % (df.FormattedID,new_data['ts']['Build'],ts.FormattedID,tc.FormattedID)) 
                            df_obj=defect(self.rally,update_df)
                            df_obj.updateDF()   

                            #update test case result
                            tcr=testCaseResult(self.rally,dic)                
                            #tr=self.rally.put('TestCaseResult', dic)
                            tr=tcr.createTCResult() 
                            trs.append(tr)  
                            break
                                                   

                if verd[0] == 1:
                    dic['tcresult'] = {'TestCase':tc._ref,'Verdict':u'Pass','Build':new_data["ts"]["Build"],'Date':datetime.datetime.now().isoformat(),'TestSet':ts._ref,'Tester':ur._ref,'Notes':verd[1]}
                    num_pass=num_pass+1

                    #update test case result
                    tcr=testCaseResult(self.rally,dic)                
                    #tr=self.rally.put('TestCaseResult', dic)
                    tr=tcr.createTCResult() 
                    trs.append(tr)          

                if verd[0] == 2:
                    dic['tcresult'] = {'TestCase':tc._ref,'Verdict':u'Blocked','Build':new_data["ts"]["Build"],'Date':datetime.datetime.now().isoformat(),'TestSet':ts._ref,'Tester':ur._ref,'Notes':verd[1]}  
                    #update test case result
                    tcr=testCaseResult(self.rally,dic)                
                    tr=tcr.createTCResult()    
                    trs.append(tr) 
                                 
            if num_pass == len(tc_verds):
                ts_obj.updateSS(1) 

            else:
                ts_obj.updateSS(2)       
            self.logger.info("The test set %s on Rally is successfully updated with test execution information" % ts.FormattedID)     
        except Exception,details:
            self.logger.error("Error: %s\n" % details,exc_info=True)
        return trs
        
    #Generate report
    def genReport(self,trs):
        filename="Report-%s.log" % datetime.datetime.now()
        try:
            with open(filename,"ab+") as f:
                i=0
                for tr in trs:
                    if i == 0:
                        f.write("Test Report for Test Set %s:\n" % tr.TestSet.FormattedID)
                        i+=1                       
                    f.write("Test Case ID: %s\nBuild: %s\nVerdict: %s\nDate: %s\nTester: %s\n" % (tr.TestCase.FormattedID,tr.Build,tr.Verdict,tr.Date,tr.Tester.UserName))
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
    # Also, the current smtp server of spirent doesnot allow sending email to email address outside the spirent domain.
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
            smtpObj.sendmail(msg["From"], msg["To"].split(','), msg.as_string())
            #close connection and session.
            smtpObj.quit()
            #print "The report is successfully sent"
            #print "--------------------------------------------------------------------"
            self.logger.info("The report is successfully sent")
        except SMTPException as error:
            #print "Error: unable to send email :  {err}".format(err=error)
            self.logger.error("Error: unable to send email :  {err}".format(err=error),exc_info=True)

