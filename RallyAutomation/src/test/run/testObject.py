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
import inspect
from buildDefinition import buildDefinition
from build import build
#from matplotlib.cbook import Null

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
    
    def sanityCheck(self):
        try:
            pass
            #raise Exception
        except Exception, details:

            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
        self.logger.info("Sanity check is successfully performed")
        return True
    
    
    #Get build information
    def getBuildInfo(self):
        try:
            builddf_obj=buildDefinition(self.rally,self.data)
            builddf=builddf_obj.getBuildDefinitionByName()
            data_with_bddf_ref=deepcopy(self.data)
            data_with_bddf_ref['build'].update({'BuildDefinition':builddf._ref})
            build_obj=build(self.rally,data_with_bddf_ref)
            bd=build_obj.getBuild()
            #self.data['ts']['Build']=build.Number
            self.logger.info("Build name %s number %s is obtained" % (bd.Name, bd.Number))

            if bd.Status=="SUCCESS":
                return
            else: raise Exception('Build failed')

        except Exception, details:

            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)


    #Get build information
    def getLatestBuild(self):
        try:
            builddf_obj=buildDefinition(self.rally,self.data)
            builddf=builddf_obj.getBuildDefinitionByName()
            data_with_bddf_ref=deepcopy(self.data)
            data_with_bddf_ref['build'].update({'BuildDefinition':builddf._ref})
            build_obj=build(self.rally,data_with_bddf_ref)
            bds=build_obj.getAllBuilds()
            sorted_bds=sorted(bds, key=lambda x: x.CreationDate, reverse=True)
            bd=sorted_bds[0]
            #build_number=bd.number
            self.data['ts']['Build']=bd.Number
            self.logger.info("Latest build name %s number %s is obtained" % (bd.Name, bd.Number))
            
            if bd.Status=="SUCCESS":
                return
            else: raise Exception('Build failed')

        except Exception, details:

            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)                
    
    #Copy test set
    def copyTS(self):
        try:
            ts_obj=testSet(self.rally,self.data)
            (ts_origin,ts_origin_dic)=ts_obj.getTSByID()
            ts_dst=ts_obj.createTS(ts_origin_dic)
            ts_new=ts_obj.addTCs(ts_origin,ts_dst)
            self.logger.info("Test set %s is copied to test set %s" % (ts_origin.FormattedID, ts_dst.FormattedID))
            #self.data['ts']={}
            #self.data['ts']['FormattedID']=ts_dst.FormattedID
            #self.logger.info("The test set is successfully copied")
            return ts_new
        except Exception, details:

            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)

    #Test execution
    def executor(self,tc,s_ession):
        try:
            #lst=tc.c_QATCPARAMSSTRING.split('|')
            lst=tc.c_QATCPARAMSTEXT.split('|')
            if lst[1]!= u'':
                lst[1]=self.data['env']['ControllerURL']+lst[1]
            if lst[6]!= u'':
                lst[6]=self.data['env']['ControllerURL']+lst[6]
            if lst[10]!= u'':
                lst[10]=self.data['env']['ControllerURL']+lst[10]

            if lst[0] == "GET":
                r = s_ession.get(lst[1])                        
            if lst[0] == "POST":#only support http for now, verify = false
                r = s_ession.post(lst[1],data=ast.literal_eval(lst[2]),verify=False)
            if lst[0] == "DELETE":
                r = s_ession.delete(lst[1])
            if lst[0] == "PUT":#only support http for now, verify = false
                r = s_ession.put(lst[1],data=ast.literal_eval(lst[2]),verify=False)
            
            self.logger.debug("The test case %s for build %s is executed." % (tc.FormattedID,self.data["ts"]["Build"]))       
            return (r,lst) 
        except Exception, details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1) 
    
    #First level check
    def firstLevelCheck(self,lst,r,verdict,tc,s_ession):
        try: 
            if r.status_code != int(lst[3]):

                #Run Env Sanity Check
                #to_obj=testObject(self.rally,self.data)       
                if self.sanityCheck():
                    verdict.append((0,'Failure: status code unexpected')) 
                    self.logger.debug("Test case %s, build %s failed because status code unexpected" % (tc.FormattedID,self.data["ts"]["Build"]))                       
                    #return verdict
                else:    
                    raise Exception('Environment sanity check failed')
                    #verdict.append((0,'Failure: sanity check of environment failed'))            
            else:
                if (lst[4] != u'' ):# and (r.content==str(lst[4])):
                    #if 'message' in r.content:
                    ver_point = ast.literal_eval(lst[4])
                    r_ver_content=deepcopy(r.content)
                    r1= r_ver_content.replace("true","\"true\"")
                    r2= r1.replace("false","\"false\"")    
                    r_ver_content=ast.literal_eval(r2)
                    for key in ver_point:                                    
                        if not ((key in r_ver_content) and (ver_point[key]==r_ver_content[key])):
                            verdict.append((0,'Failure: status code expected but first level check failed'))
                            #verified=False
                            self.logger.debug("Test case %s, build %s failed because first level check failed" % (tc.FormattedID,self.data["ts"]["Build"]))   
                            break                  
                    else:                                    
                        #verified=True
                        z=ast.literal_eval(lst[4])
                        if 'message' in r.content:
                            verdict.append((1,'Success: status code expected and first level check succeed. Message: '+z['message']))
                        else:
                            verdict.append((1,'Success: status code expected and first level check succeed.'))
                        self.logger.debug("First level check for Test case %s, build %s is successful." % (tc.FormattedID,self.data["ts"]["Build"]))
                else:
                    verdict.append((1,'Success: status code expected without first level check.'))
                    self.logger.debug("Test case %s, build %s is successful without first level check." % (tc.FormattedID,self.data["ts"]["Build"]))
                    '''
                    #else: 
                    x=r.content
                    y=str(lst[4])
                    if x==y:
                        if (ast.literal_eval(lst[4])['message'] != None):
                            z=ast.literal_eval(lst[4])
                            verdict.append((1,'Success: status code expected without verification. Message: '+z['message']) )
                    else:
                        #Run Env Sanity Check
                        #to_obj=testObject(self.rally,self.data)       
                        if self.sanityCheck():
                            verdict.append((0,'Failure: status code expected but message unexpected')) 
                        else:    
                            raise Exception('Environment sanity check failed')
                            #verdict.append((0,'Failure: sanity check of environment failed'))     
                    '''           
            
            return verdict
        except Exception, details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)           
    
    #search dictionary recursively
    def searchDict(self,dict1,dict2):
        try:
            for item2 in dict2.items():                
                for item1 in dict1.items():
                    if item2[0]==item1[0]:
                        if (type(item2[1]) != dict):
                            if item2[1]==dict1[item1[0]]:
                                #verified=True
                                status=1
                                #verdict[-1]=(verdict[-1][0],verdict[-1][1]+' Verification is successful.')
                                #verdict.append((1,'Success: status code expected and verified'))
                                #self.logger.debug("The test execution for test case %s, build %s is verified to be successful." % (tc.FormattedID,self.data["ts"]["Build"]))  
                                break         
                            else: 
                                status=2
                                #verdict[-1]=(0,'Failure: verification failed')
                                #verified=False
                                #self.logger.debug("The test execution for test case %s, build %s is verified to be failed." % (tc.FormattedID,self.data["ts"]["Build"]))   
                                return status   
                        else:
                            return self.searchDict(item1[1],item2[1])
                            #break
                            
                else:
                    status=2
                    #verdict[-1]=(0,'Failure: verification failed')
                    #verified=False
                    #self.logger.debug("The test execution for test case %s, build %s is verified to be failed." % (tc.FormattedID,self.data["ts"]["Build"]))   
                    return status                           
            return status
        except Exception, details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)     

    
    #Test verification:
    def verificator(self,lst,r,verdict,tc,s_ession):
        try:
            #Verification
            '''
            if r.status_code != int(lst[3]):

                #Run Env Sanity Check
                #to_obj=testObject(self.rally,self.data)       
                if self.sanityCheck():
                    verdict.append((0,'Failure: status code unexpected')) 
                else:    
                    raise Exception('Environment sanity check failed')
                    #verdict.append((0,'Failure: sanity check of environment failed'))
                   
            else:
                if (lst[4] != u'' ):# and (r.content==str(lst[4])):
                    x=r.content
                    y=str(lst[4])
                    if x==y:
                        if (ast.literal_eval(lst[4])['message'] != None):
                            z=ast.literal_eval(lst[4])
                            verdict.append((1,'Success: status code expected without verification. Message: '+z['message']) )
                    else:
                        #Run Env Sanity Check
                        #to_obj=testObject(self.rally,self.data)       
                        if self.sanityCheck():
                            verdict.append((0,'Failure: status code expected but message unexpected')) 
                        else:    
                            raise Exception('Environment sanity check failed')
                            #verdict.append((0,'Failure: sanity check of environment failed'))
            '''
            if (lst[7]==u"" or lst[5]==u"" or lst[6]==u""):
                self.logger.debug("As not enough verification information is provided, the test execution for test case %s, build %s is not verified" % (tc.FormattedID,self.data["ts"]["Build"]))
                verdict[-1]=(verdict[-1][0],verdict[-1][1]+' No verification is done.')
            else:    
                if lst[7] == "GET":
                    r_ver = s_ession.get(lst[6])                        
                if lst[7] == "POST":
                    r_ver = s_ession.post(lst[6],data=ast.literal_eval(lst[8]))
                if lst[7] == "DELETE":
                    r_ver = s_ession.delete(lst[6])
                if lst[7] == "PUT":
                    r_ver = s_ession.put(lst[6],data=ast.literal_eval(lst[8]))
            
                ver_point = ast.literal_eval(lst[5])
                r_ver_content=deepcopy(r_ver.content)
                r1= r_ver_content.replace("true","\"true\"")
                r2= r1.replace("false","\"false\"")    
                r_ver_content=ast.literal_eval(r2)
                #keys_ver_point,values_ver_point=ver_point.keys(),ver_point.values()
                #keys_r_ver_content,values_r_ver_content=r_ver_content.keys(),r_ver_content.values()
                                
                status=self.searchDict(r_ver_content,ver_point)
                if status==1:
                    verdict[-1]=(verdict[-1][0],verdict[-1][1]+' Verification is successful.')
                    #verdict.append((1,'Success: status code expected and verified'))
                    self.logger.debug("The test execution for test case %s, build %s is verified to be successful." % (tc.FormattedID,self.data["ts"]["Build"]))                  
                if status==2:
                    verdict[-1]=(0,'Failure: verification failed')
                    self.logger.debug("The test execution for test case %s, build %s is verified to be failed." % (tc.FormattedID,self.data["ts"]["Build"]))   
                '''
                for key in ver_point:                                    
                    if not (key in r_ver_content):
                        verdict[-1]=(0,'Failure: verification failed')
                        #verified=False
                        self.logger.debug("The test execution for test case %s, build %s is verified to be failed." % (tc.FormattedID,self.data["ts"]["Build"]))   
                        break                  
                    elif not (ver_point[key]==r_ver_content[key]):
                        if type(ver_point[key]) is dict and type(r_ver_content[key]) is dict:
                            for k in ver_point[key]:
                                if not ((k in r_ver_content[key]) and (ver_point[key][k]==r_ver_content[key][k])): 
                                    verdict[-1]=(0,'Failure: verification failed')
                                    #verified=False
                                    self.logger.debug("The test execution for test case %s, build %s is verified to be failed." % (tc.FormattedID,self.data["ts"]["Build"]))   
                                    break   
                            else:                                    
                                #verified=True
                                verdict[-1]=(verdict[-1][0],verdict[-1][1]+' Verification is successful.')
                                #verdict.append((1,'Success: status code expected and verified'))
                                self.logger.debug("The test execution for test case %s, build %s is verified to be successful." % (tc.FormattedID,self.data["ts"]["Build"]))  
                                break                              
                        else: 
                            verdict[-1]=(0,'Failure: verification failed')
                            #verified=False
                            self.logger.debug("The test execution for test case %s, build %s is verified to be failed." % (tc.FormattedID,self.data["ts"]["Build"]))   
                            break     
                        break         
                else:                                    
                    #verified=True
                    #verdict.append((1,'Success: status code expected and verified'))
                    verdict[-1]=(verdict[-1][0],verdict[-1][1]+' Verification is successful.')
                    self.logger.debug("The test execution for test case %s, build %s is verified to be successful." % (tc.FormattedID,self.data["ts"]["Build"]))
            
                
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
                '''
            return verdict
        except Exception, details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)                       
        
    #Cleanup
    def cleaner(self,lst,tc,ts,s_ession):
        try:
            if lst[10]==u"":
                self.logger.debug("As not enough cleanup information is provided, the test cleanup for test case %s, build %s, test set %s is skipped" % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))
            else: 
                if lst[9] == "GET":
                    r_clr = s_ession.get(lst[10])                        
                if lst[9] == "POST":
                    r_clr = s_ession.post(lst[10],data=ast.literal_eval(lst[11]))
                if lst[9] == "DELETE":
                    r_clr = s_ession.delete(lst[10])
                if lst[9] == "PUT":
                    r_clr = s_ession.put(lst[10],data=ast.literal_eval(lst[11]))
                
                if int(lst[12])==r_clr.status_code:              
                    self.logger.debug("The test case %s for build %s in test set %s is cleaned up successfully." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))       
                else: 
                    raise Exception("The test case %s for build %s in test set %s is failed to clean up." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))
                    #self.logger.debug("The test case %s for build %s in test set %s is failed to clean up." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))       
             
        except Exception, details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
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
                            verdict.append((2,'Blocked: the test case is blocked in last test run with same build id %s' % self.data["ts"]["Build"]))
                            self.logger.debug("The test case %s is blocked for build %s, will skip it." % (tc.FormattedID,self.data["ts"]["Build"]))
                            break
                        else:
                            s = requests.session()
                            (response,lst_of_par)=self.executor(tc,s)
                            verdict=self.firstLevelCheck(lst_of_par, response, verdict, tc,s)
                            if verdict[-1][0]!=0:
                                verdict=self.verificator(lst_of_par, response, verdict, tc,s)
                            self.cleaner(lst_of_par, tc,testset_under_test,s)
                            break
                            
                            
                else:
                    s = requests.session()
                    (response,lst_of_par)=self.executor(tc,s)
                    verdict=self.firstLevelCheck(lst_of_par, response, verdict, tc,s)
                    if verdict[-1][0]!=0:
                        verdict=self.verificator(lst_of_par, response, verdict, tc,s)
                    self.cleaner(lst_of_par, tc,testset_under_test,s)
            
            #Update ScheduleState of Test Set 
            new_data=deepcopy(self.data) 
            new_data['ts']['FormattedID']=testset_under_test.FormattedID
            ts_obj=testSet(self.rally,new_data)
            ts_obj.updateSS(0) 
                    
            #verdict=[0,1,1]
            #verdict=[(0,"Failure reason 3"),(1,"Success reason 3"),(0,"Failure reason 4"),(1,"Success reason 4")]
            self.logger.info("The test run is successfully executed on Chasis")
        except Exception,details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
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
                                                   

                elif verd[0] == 1:
                    dic['tcresult'] = {'TestCase':tc._ref,'Verdict':u'Pass','Build':new_data["ts"]["Build"],'Date':datetime.datetime.now().isoformat(),'TestSet':ts._ref,'Tester':ur._ref,'Notes':verd[1]}
                    num_pass=num_pass+1

                    #update test case result
                    tcr=testCaseResult(self.rally,dic)                
                    #tr=self.rally.put('TestCaseResult', dic)
                    tr=tcr.createTCResult() 
                    trs.append(tr)          

                elif verd[0] == 2:
                    dic['tcresult'] = {'TestCase':tc._ref,'Verdict':u'Blocked','Build':new_data["ts"]["Build"],'Date':datetime.datetime.now().isoformat(),'TestSet':ts._ref,'Tester':ur._ref,'Notes':verd[1]}  
                    #update test case result
                    tcr=testCaseResult(self.rally,dic)                
                    tr=tcr.createTCResult()    
                    trs.append(tr) 
                
                else:
                    dic['tcresult'] = {'TestCase':tc._ref,'Verdict':u'Error','Build':new_data["ts"]["Build"],'Date':datetime.datetime.now().isoformat(),'TestSet':ts._ref,'Tester':ur._ref,'Notes':'Unexpected verdict'}  
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
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
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
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
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
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error("Error: unable to send email :  {err}".format(err=error),exc_info=True)
                sys.exit(1)
            #print "Error: unable to send email :  {err}".format(err=error)
            

