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
import json
import constants
import re

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
    
    
    #Update build info
    def updateBuildInfo(self):
        try:
            builddf_obj=buildDefinition(self.rally,self.data)
            builddfs=builddf_obj.getAllBuildDefinitions()
            for builddf in builddfs:
                if builddf.Name == self.data['builddf']['Name']:
                    break
            else:   
                new_builddf=builddf_obj.createBuildDefinition()
                self.logger.info("New build definition name %s is created" % (new_builddf.Name))
            
            data_with_bddf_ref=deepcopy(self.data)
            data_with_bddf_ref['build'].update({'BuildDefinition':builddf._ref})
            build_obj=build(self.rally,data_with_bddf_ref)
            bd=build_obj.createBuild()
            #self.data['ts']['Build']=build.Number
            self.logger.info("Build name %s number %s is created" % (bd.Name, bd.Number))

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
            (ts_origin,ts_origin_dic)=ts_obj.getTSByID(self.data['ts']['FormattedID'])
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

    #Replace variable
    def rep(self,strg,variable_value_dict):
        varbs=[]
        i=0
        verd=True
        missing_varbs=[]
        while True:
        #for i in xrange(0,len(strg)):
            if strg[i]=='$':
                varb=re.split('[^a-zA-Z0-9_\[\]]+',strg[i:].partition('$')[-1])[0]
                varbs.append(varb)#partition('[\n\/\\\b\&\?\;\=\,\"]')[0])
                if varbs[-1] in self.data['env']:
                    strg=strg.replace('$'+varbs[-1],self.data['env'][varbs[-1]])
                elif varbs[-1] in self.data['accounts']:
                    strg=strg.replace('$'+varbs[-1],self.data['accounts'][varbs[-1]])
                elif varbs[-1] in variable_value_dict:
                    strg=strg.replace('$'+varbs[-1],variable_value_dict[varbs[-1]])
                else:
                    verd=False
                    missing_varbs.append(varb)
                    #return False,strg,varbs
            if len(strg)==i+1:    
                break            
                #return True,strg,varbs
            i+=1
        return verd,strg,varbs,missing_varbs
    
    #Setup
    def setup(self,lst,tc,ts,s_ession,variable_value_dict):
        try:
            '''
            if lst[constants.INDEXES_EXE[1]]!= u'':
                lst[constants.INDEXES_EXE[1]]=self.data['env']['ControllerURL']+lst[constants.INDEXES_EXE[1]]
            if lst[constants.INDEXES_VER[0]]!= u'':
                lst[constants.INDEXES_VER[0]]=self.data['env']['ControllerURL']+lst[constants.INDEXES_VER[0]]
            if lst[constants.INDEXES_CLU[0]]!= u'':
                lst[constants.INDEXES_CLU[0]]=self.data['env']['ControllerURL']+lst[constants.INDEXES_CLU[0]]
            '''
            if lst[constants.INDEXES_SUP[1]]!=u'':
                lst[constants.INDEXES_SUP[1]]=self.data['env']['ControllerURL']+lst[constants.INDEXES_SUP[1]]            
            
            verdict=None
            r_stp=None
            if lst[constants.INDEXES_SUP[0]]==u"":
                self.logger.debug("As not enough setup information is provided, the test setup for test case %s build %s  test set %s is skipped" % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))
            else: 
                '''
                if '$' in lst[constants.INDEXES_EXE[1]]:
                    rep_status,lst[constants.INDEXES_EXE[1]]=self.rep(lst[constants.INDEXES_EXE[1]],tc,ts)
                    if rep_status==False:
                        return False,lst
                if '$' in lst[constants.INDEXES_VER[0]]:
                    rep_status,lst[constants.INDEXES_VER[0]]=self.rep(lst[constants.INDEXES_VER[0]],tc,ts)
                    if rep_status==False:
                        return False,lst                                       
                if '$' in lst[constants.INDEXES_CLU[0]]:
                    rep_status,lst[constants.INDEXES_CLU[0]]=self.rep(lst[constants.INDEXES_CLU[0]],tc,ts)
                    if rep_status==False:
                        return False,lst
                if '$' in lst[constants.INDEXES_SUP[0]]:
                    rep_status,lst[constants.INDEXES_SUP[0]]=self.rep(lst[constants.INDEXES_SUP[0]],tc,ts)
                    if rep_status==False:
                        return False,lst
                '''
                missing_varbs_string=""
                for idx in constants.INDEXES_SUP:
                    if '$' in lst[idx]:
                        rep_status,lst[idx],varbs,missing_varbs=self.rep(lst[idx],variable_value_dict)
                        if rep_status==False:
                            missing_varbs_string=missing_varbs[0]
                            for i in missing_varbs:
                                if len(missing_varbs)==1:                                    
                                    break
                                if missing_varbs.index(i)>0:
                                    missing_varbs_string=missing_varbs_string+", "+i
                            #raise Exception("The test case %s for build %s in test set %s is failed to setup because %s in extra.json is not defined." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID,varbs[-1]))
                            if len(missing_varbs)==1:
                                self.logger.debug("The test case %s for build %s in test set %s is failed to setup because %s is/are not defined in extra.json or pre-defined local variables." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID,missing_varbs_string))    
                            return False,lst,variable_value_dict                            
                        
                if lst[constants.INDEXES_SUP[0]] == "GET":
                    r_stp = s_ession.get(lst[constants.INDEXES_SUP[1]])                        
                elif lst[constants.INDEXES_SUP[0]] == "POST":
                    r_stp = s_ession.post(lst[constants.INDEXES_SUP[1]],data=json.loads(lst[constants.INDEXES_SUP[2]]))
                elif lst[constants.INDEXES_SUP[0]] == "DELETE":
                    r_stp = s_ession.delete(lst[constants.INDEXES_SUP[1]])
                elif lst[constants.INDEXES_SUP[0]] == "PUT":
                    r_stp = s_ession.put(lst[constants.INDEXES_SUP[1]],data=json.loads(lst[constants.INDEXES_SUP[2]]))
                else:
                    #check if lst[constants.INDEXES_CLU[4]] is api level test case, if it does run api level test case
                    apits_id=self.data['apits']['FormattedID']
                    ts_obj=testSet(self.rally,self.data)
                    ts_api=ts_obj.getTSByID(apits_id)[0]
                    
                    
                    for tc_api in ts_api.TestCases:
                        if tc_api.Name==lst[constants.INDEXES_SUP[0]]:
                            verdict,variable_value_dict=self.runTC(tc_api, [], ts_api,constants.STEPS_SUP_EXE_FLC_VER,variable_value_dict,s_ession,lst[constants.INDEXES_SUP[2]])
                            break
                    else:
                        self.logger.debug("The test case %s for build %s in test set %s is failed to setup because the api call is unexpected." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))    
                        return False,lst,variable_value_dict 
                        
                if r_stp!=None:
                    if r_stp.status_code != int(lst[constants.INDEXES_SUP[3]]):
                        self.logger.debug("The test case %s for build %s in test set %s is failed to setup because status code is unexpected." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))    
                        return False,lst,variable_value_dict          
                    else:
                        if (lst[constants.INDEXES_SUP[4]] != u'' ):
                            '''
                            ver_point = ast.literal_eval(lst[constants.INDEXES_SUP[1]])
                            r_ver_content=deepcopy(r_stp.content)
                            r1= r_ver_content.replace("true","\"true\"")
                            r2= r1.replace("false","\"false\"")    
                            r_ver_content=ast.literal_eval(r2)
                            '''
                            ver_point=deepcopy(json.loads(lst[constants.INDEXES_SUP[4]]))
                            r_ver_content=deepcopy(json.loads(r_stp.content))
                            
                            error_message=self.searchDict2(ver_point,r_ver_content,"")
                            if error_message=='':
                                self.logger.debug("The test case %s for build %s in test set %s is setup successfully." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))
                            else:
                                self.logger.debug("The test case %s for build %s in test set %s is failed to setup because the content of response body is unexpected" % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))   
                                return False,lst,variable_value_dict
                        else:
                            self.logger.debug("The test case %s for build %s in test set %s is setup successfully." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))       
            
                if verdict != None:
                    if verdict[0][0]==1:
                        self.logger.debug("The test case %s for build %s in test set %s is setup successfully." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))       
                    else:
                        self.logger.debug("The test case %s for build %s in test set %s is failed to setup because the restful api level test case %s (%s) failed: %s" % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID,tc_api.FormattedID,tc_api.Name,verdict[0][1]))   
                        return False,lst,variable_value_dict                            
                    
            return True,lst,variable_value_dict 
        except Exception, details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)       
        
    

    #Test execution
    def executor(self,lst,tc,s_ession,variable_value_dict,request_to_sub):
        try:
            #lst=tc.c_QATCPARAMSSTRING.split('|')
            '''
            if lst[constants.INDEXES_EXE[1]]!= u'':
                lst[constants.INDEXES_EXE[1]]=self.data['env']['ControllerURL']+lst[constants.INDEXES_EXE[1]]
            if lst[constants.INDEXES_FLC[2]]!= u'':
                lst[constants.INDEXES_FLC[2]]=self.data['env']['ControllerURL']+lst[constants.INDEXES_FLC[2]]
            if lst[constants.INDEXES_VER[3]]!= u'':
                lst[constants.INDEXES_VER[3]]=self.data['env']['ControllerURL']+lst[constants.INDEXES_VER[3]]
            '''          
              
            if lst[constants.INDEXES_EXE[1]]!= u'':
                lst[constants.INDEXES_EXE[1]]=self.data['env']['ControllerURL']+lst[constants.INDEXES_EXE[1]]            

            if len(request_to_sub)!=0:
                lst[constants.INDEXES_EXE[2]]=request_to_sub
            
            missing_varbs_string=""
            for idx in constants.INDEXES_EXE:
                if '$' in lst[idx]:
                    rep_status,lst[idx],varbs,missing_varbs=self.rep(lst[idx],variable_value_dict)
                    if rep_status==False:
                        missing_varbs_string=missing_varbs[0]
                        for i in missing_varbs:
                            if len(missing_varbs)==1:                                    
                                break
                            if missing_varbs.index(i)>0:
                                missing_varbs_string=missing_varbs_string+", "+i
                        #raise Exception("The test case %s for build %s is failed to execute because %s in extra.json is not defined." % (tc.FormattedID,self.data["ts"]["Build"],varbs[-1]))
                        self.logger.debug("The test case %s for build %s is failed to execute because %s is/are not defined in extra.json or pre-defined local variables." % (tc.FormattedID,self.data["ts"]["Build"],missing_varbs_string))    
                        return False,lst,variable_value_dict  
            
            json_request={}      
            if lst[constants.INDEXES_EXE[1]] !="":                                     
                if lst[constants.INDEXES_EXE[0]] == "GET":
                    r = s_ession.get(lst[constants.INDEXES_EXE[1]])                        
                elif lst[constants.INDEXES_EXE[0]] == "POST":#only support http for now, verify = false
                    if lst[constants.INDEXES_EXE[2]]!='':
                        json_request=json.loads(lst[constants.INDEXES_EXE[2]])
                    #try:                    
                        r = s_ession.post(lst[constants.INDEXES_EXE[1]],data=json_request,verify=False)
                    #except Exception,details:
                    else:
                        return False,lst,variable_value_dict 
                elif lst[constants.INDEXES_EXE[0]] == "DELETE":
                    r = s_ession.delete(lst[constants.INDEXES_EXE[1]])
                elif lst[constants.INDEXES_EXE[0]] == "PUT":#only support http for now, verify = false
                    if lst[constants.INDEXES_EXE[2]]!='':
                        json_request=json.loads(lst[constants.INDEXES_EXE[2]])                
                        r = s_ession.put(lst[constants.INDEXES_EXE[1]],data=json_request,verify=False)
                    else:
                        return False,lst,variable_value_dict                       
                else:
                    #raise Exception("Unexpected execution method: %s" % lst[constants.INDEXES_EXE[0]])
                    self.logger.debug("Unexpected execution method: %s" % lst[constants.INDEXES_EXE[0]])    
                    return False,lst,variable_value_dict  
            else:
                self.logger.debug("No path is provided")    
                return False,lst,variable_value_dict
            
            #save values in json request into variables
            if len(json_request)!=0:
                variable_list=[]
                if lst[constants.INDEXES_EXE[3]]!="":
                    variable_list=lst[constants.INDEXES_EXE[3]].split(';')
                    
                    for varb in variable_list:
                        values=self.searchKeyInDic(json_request, varb)
                        i=0
                        if len(values)==0:
                            self.logger.debug("Failed to save values in requested json object to varaible %s as it cannot be found in the requested json object" % varb)       
                            return False,lst,variable_value_dict                   
                        while i < len(values) and len(values)>1:
                            if values[i]!=values[i+1]:                            
                                self.logger.debug("Failed to save values in response content to varaible %s as there are multiple different values for it in response" % varb)  
                                return False,lst,variable_value_dict                             
                            i+=1
                        else:
                            variable_value_dict[varb]=values[0] 
                            self.logger.debug("Successfully save values in response content to variable: %s" % varb)  
                               
            self.logger.debug("The test case %s for build %s is executed." % (tc.FormattedID,self.data["ts"]["Build"]))       
            return (r,lst,variable_value_dict) 
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
    
    def searchDict2(self,d1, d2, error_message):
        #print "Changes in " + ctx
        for k in d1:
            if k not in d2:
                #print "%s:%s is missing from content of response" % (k,d1[k])
                error_message+= " '"+k+"' : "+str(d1[k])+" is missing from content of response."
        for k in d2:
            
            if k not in d1:
                #print k + " added in d2"
                continue
            
            if d2[k] != d1[k]:
                if type(d2[k]) != dict:
                    #print "%s:%s is different in content of response" % (k,str(d2[k]))
                    error_message+= " '"+k+"' : "+str(d2[k])+" in content of response is different from the expected." 
                else:
                    if type(d1[k]) != type(d2[k]):
                        error_message+= " '"+k+"' : "+str(d2[k])+" in content of response is different from the expected." 
                        continue
                    else:
                        if type(d2[k]) == dict:
                            error_message=self.searchDict2(d1[k], d2[k],error_message)
                            continue
        #print "Done with changes in " + ctx
        return error_message

    def searchKeyInDic(self,search_dict, field):
        """
        Takes a dict with nested lists and dicts,
        and searches all dicts for a key of the field
        provided.
        """
        fields_found = []
    
        for key, value in search_dict.iteritems():
    
            if key == field:
                fields_found.append(value)
    
            elif isinstance(value, dict):
                results = self.searchKeyInDic(value, field)
                for result in results:
                    fields_found.append(result)
    
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        more_results = self.searchKeyInDic(item, field)
                        for another_result in more_results:
                            fields_found.append(another_result)
    
        return fields_found
    
    
    #First level check
    def firstLevelCheck(self,lst,r,verdict,tc,s_ession,variable_value_dict):
        try: 
            #ver_point = ast.literal_eval(lst[constants.INDEXES_FLC[0]])

            #r1= r_ver_content.replace("true","\"true\"")
            #r2= r1.replace("false","\"false\"")    
            #r_ver_content=ast.literal_eval(r2)            
            missing_varbs_string=""
            for idx in constants.INDEXES_FLC:
                if '$' in lst[idx]:
                    rep_status,lst[idx],varbs,missing_varbs=self.rep(lst[idx],variable_value_dict)
                    if rep_status==False:
                        missing_varbs_string=missing_varbs[0]
                        for i in missing_varbs:
                            if len(missing_varbs)==1:                                    
                                break
                            if missing_varbs.index(i)>0:
                                missing_varbs_string=missing_varbs_string+", "+i
                        #raise Exception("The test case %s for build %s is failed to pass first level check because %s in extra.json is not defined." % (tc.FormattedID,self.data["ts"]["Build"],varbs[-1]))
                        verdict.append((constants.BLOCKED,'Blocked: %s is/are not defined in extra.json or pre-defined local variables' % missing_varbs_string)) 
                        self.logger.debug("The test case %s for build %s is failed to pass first level check because %s is/are not defined in extra.json or pre-defined local variables." % (tc.FormattedID,self.data["ts"]["Build"],missing_varbs_string))    
                        return verdict,variable_value_dict  
                        
                        
            if not(lst[constants.INDEXES_FLC[0]].isdigit()):
                verdict.append((constants.BLOCKED,'Blocked: status code is expected to be digits instead of something else: %s' % lst[constants.INDEXES_FLC[0]])) 
                self.logger.debug("The test case %s for build %s failed to pass first level check because status code is expected to be digits instead of something else: %s" % (tc.FormattedID,self.data["ts"]["Build"],lst[constants.INDEXES_FLC[0]]))    
                return verdict,variable_value_dict                  
            
            elif (lst[constants.INDEXES_FLC[0]].isdigit()) and r.status_code != int(lst[constants.INDEXES_FLC[0]]):
                #Run Env Sanity Check
                #to_obj=testObject(self.rally,self.data)       
                if self.sanityCheck():
                    verdict.append((constants.FAILED,'Failure: status code unexpected. The unexpected status code of the response is %s' % r.status_code)) 
                    self.logger.debug("Test case %s, build %s failed because status code unexpected. The unexpected status code of the response is %s" % (tc.FormattedID,self.data["ts"]["Build"],r.status_code))                       
                    #return verdict
                else:    
                    raise Exception('Environment sanity check failed')
                    #verdict.append((0,'Failure: sanity check of environment failed'))            
            else:
                r_ver_content=deepcopy(json.loads(r.content))

                if (lst[constants.INDEXES_FLC[1]] != u'' ):# and (r.content==str(lst[constants.INDEXES_FLC[0]])):
                    ver_point=deepcopy(json.loads(lst[constants.INDEXES_FLC[1]]))
                    error_message=self.searchDict2(ver_point,r_ver_content,"")
                    if error_message=='':
                        #First level check succeed
                        #z=ast.literal_eval(lst[constants.INDEXES_FLC[0]])
                        if 'message' in r.content:
                            verdict.append((constants.SUCCESS,'Success: status code expected and first level check succeed. Message: '+ver_point['message']))
                        else:
                            verdict.append((constants.SUCCESS,'Success: status code expected and first level check succeed.'))
                        self.logger.debug("First level check for Test case %s, build %s is successful." % (tc.FormattedID,self.data["ts"]["Build"]))
                    else:
                        #First level check failed
                        verdict.append((constants.FAILED,'Failure: status code expected but first level check failed. Error:%s' % error_message))
                        self.logger.debug("Test case %s, build %s failed because first level check failed. Error: %s" % (tc.FormattedID,self.data["ts"]["Build"],error_message))   
                    

                else:
                    verdict.append((constants.SUCCESS,'Success: status code expected without first level check.'))
                    self.logger.debug("Test case %s, build %s is successful without first level check." % (tc.FormattedID,self.data["ts"]["Build"]))
         
                #save values in response into variables
                variable_list=[]
                if lst[constants.INDEXES_FLC[2]]!="":
                    variable_list=lst[constants.INDEXES_FLC[2]].split(';')
                    #variable_value_dict={}
                    for varb in variable_list:
                        values=self.searchKeyInDic(r_ver_content, varb)
                        i=0
                        if len(values)==0:
                            verdict[-1]=(verdict[-1][0],verdict[-1][1]+' but failed to save values in response content to varaibles as the variable: %s cannot be found in the response content' % varb)
                            self.logger.debug("Failed to save values in response content to varaible %s as it cannot be found in response content" % varb)                          
                        while i < len(values) and len(values)>1:
                            if values[i]!=values[i+1]:
                                verdict[-1]=(verdict[-1][0],verdict[-1][1]+' but failed to save values in response content to varaibles as there are multiple different values for variable: %s' % varb)
                                self.logger.debug("Failed to save values in response content to varaible %s as there are multiple different values for it in response" % varb)  
                                break                             
                            i+=1
                        else:
                            variable_value_dict[varb]=values[0] 
                            self.logger.debug("Successfully save values in response content to variable: %s" % varb)  

            
            return verdict,variable_value_dict
        except Exception, details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)           
    


    
    #Test verification:
    def verificator(self,lst,r,verdict,tc,s_ession,variable_value_dict):
        try:
            if lst[constants.INDEXES_VER[1]]!= u'':
                lst[constants.INDEXES_VER[1]]=self.data['env']['ControllerURL']+lst[constants.INDEXES_VER[1]]
            
            missing_varbs_string=""
            for idx in constants.INDEXES_VER:
                if '$' in lst[idx]:
                    rep_status,lst[idx],varbs,missing_varbs=self.rep(lst[idx],variable_value_dict)
                    if rep_status==False:
                        missing_varbs_string=missing_varbs[0]
                        for i in missing_varbs:
                            if len(missing_varbs)==1:                                    
                                break
                            if missing_varbs.index(i)>0:
                                missing_varbs_string=missing_varbs_string+", "+i
                        raise Exception("The test case %s for build %s is failed to verify because %s is/are not defined in extra.json or pre-defined local variables." % (tc.FormattedID,self.data["ts"]["Build"],missing_varbs_string))
                        #self.logger.debug("The test case %s for build %s is failed to execute because %s in extra.json is not defined." % (tc.FormattedID,self.data["ts"]["Build"],varbs[-1]))    
                        #return False,lst  
                        
            if (lst[constants.INDEXES_VER[2]]==u""): #or lst[constants.INDEXES_FLC[2]]==u"" or lst[constants.INDEXES_VER[0]]==u""):
                self.logger.debug("As not enough verification information is provided, the test execution for test case %s, build %s is not verified" % (tc.FormattedID,self.data["ts"]["Build"]))
                verdict[-1]=(verdict[-1][0],verdict[-1][1]+' No verification is done.')
            else:
                r_ver=None    
                if lst[constants.INDEXES_VER[2]] == "GET":
                    r_ver = s_ession.get(lst[constants.INDEXES_VER[1]])                        
                if lst[constants.INDEXES_VER[2]] == "POST":
                    r_ver = s_ession.post(lst[constants.INDEXES_VER[1]],data=json.loads(lst[constants.INDEXES_VER[3]]))
                if lst[constants.INDEXES_VER[2]] == "DELETE":
                    r_ver = s_ession.delete(lst[constants.INDEXES_VER[1]])
                if lst[constants.INDEXES_VER[2]] == "PUT":
                    r_ver = s_ession.put(lst[constants.INDEXES_VER[1]],data=json.loads(lst[constants.INDEXES_VER[3]]))

                if r_ver!=None:
                    ver_point=deepcopy(json.loads(lst[constants.INDEXES_VER[0]]))
                    r_ver_content=deepcopy(json.loads(r_ver.content))
                    
                    error_message=self.searchDict2(ver_point,r_ver_content,"")
                    if error_message=='':
                        verdict[-1]=(verdict[-1][0],verdict[-1][1]+' Verification is successful.')
                        #verdict.append((1,'Success: status code expected and verified'))
                        self.logger.debug("The test execution for test case %s, build %s is verified to be successful." % (tc.FormattedID,self.data["ts"]["Build"]))                  
                    else:
                        verdict[-1]=(constants.FAILED,'Failure: verification failed. Error:%s' % error_message)
                        self.logger.debug("The test execution for test case %s, build %s is verified to be failed. Error: %s" % (tc.FormattedID,self.data["ts"]["Build"],error_message))   
                        
                else:
                    '''
                    ver_point = ast.literal_eval(lst[constants.INDEXES_FLC[1]])
                    r_ver_content=deepcopy(r_ver.content)
                    r1= r_ver_content.replace("true","\"true\"")
                    r2= r1.replace("false","\"false\"")    
                    r_ver_content=ast.literal_eval(r2)
                    #keys_ver_point,values_ver_point=ver_point.keys(),ver_point.values()
                    #keys_r_ver_content,values_r_ver_content=r_ver_content.keys(),r_ver_content.values()
                    '''
                    #check if lst[constants.INDEXES_VER[1]] is api level test case, if it does run api level test case
                    apits_id=self.data['apits']['FormattedID']
                    ts_obj=testSet(self.rally,self.data)
                    ts_api=ts_obj.getTSByID(apits_id)[0]
                    
                    verdict_api=None
                    for tc_api in ts_api.TestCases:
                        if tc_api.Name==lst[constants.INDEXES_VER[2]]:
                            verdict_api,variable_value_dict=self.runTC(tc_api, [], ts_api,constants.STEPS_EXE_FLC_VER,variable_value_dict,s_ession,lst[constants.INDEXES_VER[3]])
                            break
                    
                    if verdict_api!=None:
                        if verdict_api[0][0]==1:
                            verdict[-1]=(verdict[-1][0],verdict[-1][1]+' Verification is successful.')
                            self.logger.debug("The test execution of test case %s for build %s is verified to be successfully." % (tc.FormattedID,self.data["ts"]["Build"]))       
                        else:
                            verdict[-1]=(constants.FAILED,'Failure: verification failed. Error: the api level test case %s is %s' % (tc_api.Name,verdict_api[0][1]))
                            self.logger.debug("The test case %s for build %s is failed to verify because the api level test case %s (%s) failed: %s" % (tc.FormattedID,self.data["ts"]["Build"],tc_api.FormattedID,tc_api.Name,verdict_api[0][1]))   
                            #return False,lst                
                    else:
                        verdict[-1]=(constants.FAILED,'Failure: verification failed. Error: the api level test case name %s cannot be found in API test set %s' % (lst[constants.INDEXES_VER[2]],apits_id))
                        self.logger.debug("The test case %s for build %s is failed to verify because the api level test case name %s cannot be found in API test set %s" % (tc.FormattedID,self.data["ts"]["Build"],lst[constants.INDEXES_VER[2]],apits_id))   
                        
                    
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
    def cleaner(self,lst,tc,ts,s_ession,variable_value_dict):
        try:
            if lst[constants.INDEXES_CLU[1]]!= u'':
                lst[constants.INDEXES_CLU[1]]=self.data['env']['ControllerURL']+lst[constants.INDEXES_CLU[1]]
            
            missing_varbs_string=""    
            for idx in constants.INDEXES_CLU:
                if '$' in lst[idx]:
                    rep_status,lst[idx],varbs,missing_varbs=self.rep(lst[idx],variable_value_dict)
                    if rep_status==False:
                        missing_varbs_string=missing_varbs[0]
                        for i in missing_varbs:
                            if len(missing_varbs)==1:                                    
                                break
                            if missing_varbs.index(i)>0:
                                missing_varbs_string=missing_varbs_string+", "+i
                        raise Exception("The test case %s for build %s is failed to clean up because %s is/are not defined in extra.json or pre-defined local variables." % (tc.FormattedID,self.data["ts"]["Build"],missing_varbs_string))
                        #self.logger.debug("The test case %s for build %s is failed to execute because %s in extra.json is not defined." % (tc.FormattedID,self.data["ts"]["Build"],varbs[-1]))    
                        #return False,lst           
                           
            r_clr=None
            if lst[constants.INDEXES_CLU[0]]==u"":
                self.logger.debug("As not enough cleanup information is provided, the test cleanup for test case %s, build %s, test set %s is skipped" % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))
            else: 
                if lst[constants.INDEXES_CLU[0]] == "GET":
                    r_clr = s_ession.get(lst[constants.INDEXES_CLU[1]])                        
                if lst[constants.INDEXES_CLU[0]] == "POST":
                    r_clr = s_ession.post(lst[constants.INDEXES_CLU[1]],data=json.loads(lst[constants.INDEXES_CLU[2]]))
                if lst[constants.INDEXES_CLU[0]] == "DELETE":
                    r_clr = s_ession.delete(lst[constants.INDEXES_CLU[1]])
                if lst[constants.INDEXES_CLU[0]] == "PUT":
                    r_clr = s_ession.put(lst[constants.INDEXES_CLU[1]],data=json.loads(lst[constants.INDEXES_CLU[2]]))
                '''    
                if int(lst[constants.INDEXES_CLU[0]])==r_clr.status_code:              
                    self.logger.debug("The test case %s for build %s in test set %s is cleaned up successfully." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))       
                else: 
                    raise Exception("The test case %s for build %s in test set %s is failed to clean up." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))
                    #self.logger.debug("The test case %s for build %s in test set %s is failed to clean up." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))       
                '''
                if r_clr!=None:
                    if r_clr.status_code != int(lst[constants.INDEXES_CLU[3]]):
                        raise Exception("The test case %s for build %s in test set %s is failed to clean up." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))                
                    else:
                        if (lst[constants.INDEXES_CLU[4]] != u'' ):
                            '''
                            ver_point = ast.literal_eval(lst[constants.INDEXES_CLU[1]])
                            r_ver_content=deepcopy(r_clr.content)
                            r1= r_ver_content.replace("true","\"true\"")
                            r2= r1.replace("false","\"false\"")    
                            r_ver_content=ast.literal_eval(r2)
                            '''
                            ver_point=deepcopy(json.loads(lst[constants.INDEXES_CLU[4]]))
                            r_ver_content=deepcopy(json.loads(r_clr.content))
                            
                            error_message=self.searchDict2(ver_point,r_ver_content,"")
                            if error_message=='':
                                self.logger.debug("The test case %s for build %s in test set %s is cleaned up successfully." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))
                            else:
                                raise Exception("The test case %s for build %s in test set %s is failed to clean up." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))                    
                        else:
                            self.logger.debug("The test case %s for build %s in test set %s is cleaned up successfully." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))       
                else:        
                    #check if lst[constants.INDEXES_CLU[0]] is api level test case, if it does run api level test case
                    apits_id=self.data['apits']['FormattedID']
                    ts_obj=testSet(self.rally,self.data)
                    ts_api=ts_obj.getTSByID(apits_id)[0]
                    
                    verdict_api=None
                    for tc_api in ts_api.TestCases:
                        if tc_api.Name==lst[constants.INDEXES_CLU[0]]:
                            verdict_api,variable_value_dict=self.runTC(tc_api, [], ts_api,constants.STEPS_EXE_FLC_VER,variable_value_dict,s_ession,lst[constants.INDEXES_VER[3]])
                            break
                    
                    if verdict_api!=None:
                        if verdict_api[0][0]==1:
                            #verdict[-1]=(verdict[-1][0],verdict[-1][1]+' Verification is successful.')
                            self.logger.debug("The test cleanup of test case %s for build %s is successfully." % (tc.FormattedID,self.data["ts"]["Build"]))       
                        else:
                            #verdict[-1]=(constants.FAILED,'Failure: verification failed. Error: the api level test case %s is %s' % (tc_api.Name,verdict_api[0][1]))
                            raise Exception("The test case %s for build %s is failed to cleanup because the api level test case %s (%s) failed: %s" % (tc.FormattedID,self.data["ts"]["Build"],tc_api.FormattedID,tc_api.Name,verdict_api[0][1]))   
                            #return False,lst                
                    else:
                        #verdict[-1]=(constants.FAILED,'Failure: verification failed. Error: the api level test case name %s cannot be found in API test set %s' % (lst[constants.INDEXES_VER[2]],apits_id))
                        raise Exception("The test case %s for build %s is failed to clean up because the api level test case name %s cannot be found in API test set %s" % (tc.FormattedID,self.data["ts"]["Build"],lst[constants.INDEXES_CLU[0]],apits_id))   
        
                 
        except Exception, details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
    
    #run a single test case
    def runTC(self,tc,verdict,testset_under_test,steps_type,variable_value_dict,s,request_to_sub):
        if steps_type==constants.STEPS_SUP_EXE_FLC_VER_CLU: #1 means run through all steps
            lst=tc.c_QATCPARAMSTEXT.split('|')
            #s = requests.session()
            setup_result,lst,variable_value_dict=self.setup(lst, tc, testset_under_test, s,variable_value_dict)
            if setup_result==True:
                (response,lst_of_par,variable_value_dict)=self.executor(lst,tc,s,variable_value_dict,request_to_sub)
                if response==False:
                    verdict.append((constants.FAILED,'Failed: the test case failed because execution step failed'))
                    self.logger.debug("The test case %s failed for build %s in execution step, will do test cleanup directly." % (tc.FormattedID,self.data["ts"]["Build"]))
                    self.cleaner(lst_of_par, tc,testset_under_test,s,variable_value_dict)
                else:
                    verdict,variable_value_dict=self.firstLevelCheck(lst_of_par, response, verdict, tc,s,variable_value_dict)
                    if verdict[-1][0]==1:
                        verdict=self.verificator(lst_of_par, response, verdict, tc,s,variable_value_dict)
                    self.cleaner(lst_of_par, tc,testset_under_test,s,variable_value_dict)
            else:
                verdict.append((constants.BLOCKED,'Blocked: the test case is blocked because the test setup failed'))
                self.logger.debug("The test case %s is blocked for build %s, will skip it." % (tc.FormattedID,self.data["ts"]["Build"]))
            return verdict,variable_value_dict                        
        if steps_type==constants.STEPS_SUP_EXE_FLC_VER: #run only setup, execution, firstlevelcheck and verification
            lst=tc.c_QATCPARAMSTEXT.split('|')
            #s = requests.session()
            setup_result,lst,variable_value_dict=self.setup(lst, tc, testset_under_test, s,variable_value_dict)
            if setup_result==True:
                (response,lst_of_par,variable_value_dict)=self.executor(lst,tc,s,variable_value_dict,request_to_sub)
                verdict,variable_value_dict=self.firstLevelCheck(lst_of_par, response, verdict, tc,s,variable_value_dict)
                if verdict[-1][0]==1:
                    verdict=self.verificator(lst_of_par, response, verdict, tc,s,variable_value_dict)
                #self.cleaner(lst_of_par, tc,testset_under_test,s)
            else:
                verdict.append((constants.BLOCKED,'Blocked: the test case is blocked because the test setup failed'))
                self.logger.debug("The test case %s is blocked for build %s, will skip it." % (tc.FormattedID,self.data["ts"]["Build"]))
            return verdict,variable_value_dict                 

        if steps_type==constants.STEPS_EXE_FLC_VER: #run only execution, firstlevelcheck and verification
            lst=tc.c_QATCPARAMSTEXT.split('|')
            #s = requests.session()
            #setup_result,lst=self.setup(lst, tc, testset_under_test, s)
            #if setup_result==True:
            (response,lst_of_par,variable_value_dict)=self.executor(lst,tc,s,variable_value_dict,request_to_sub)
            verdict,variable_value_dict=self.firstLevelCheck(lst_of_par, response, verdict, tc,s,variable_value_dict)
            if verdict[-1][0]==1:
                verdict=self.verificator(lst_of_par, response, verdict, tc,s,variable_value_dict)
                #self.cleaner(lst_of_par, tc,testset_under_test,s)
            else:
                #verdict.append((constants.BLOCKED,'Blocked: the test case is blocked because the test setup failed'))
                if verdict[-1][0]==constants.BLOCKED:
                    self.logger.debug("The test case %s is blocked for build %s, will skip it." % (tc.FormattedID,self.data["ts"]["Build"]))
                if verdict[-1][0]==constants.FAILED:
                    self.logger.debug("The test case %s failed for build %s, will skip it." % (tc.FormattedID,self.data["ts"]["Build"]))
            return verdict,variable_value_dict    
                                    
    #run all tests in a test set     
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
                            verdict.append((constants.BLOCKED,'Blocked: the test case is blocked in last test run with same build id %s' % self.data["ts"]["Build"]))
                            self.logger.debug("The test case %s is blocked for build %s, will skip it." % (tc.FormattedID,self.data["ts"]["Build"]))
                            break
                        else:
                            
                            '''
                            lst=tc.c_QATCPARAMSTEXT.split('|')
                            
                            setup_result,lst=self.setup(lst, tc, testset_under_test, s)
                            if setup_result==True:
                                (response,lst_of_par)=self.executor(lst,tc,s)
                                verdict=self.firstLevelCheck(lst_of_par, response, verdict, tc,s)
                                if verdict[-1][0]!=0:
                                    verdict=self.verificator(lst_of_par, response, verdict, tc,s)
                                self.cleaner(lst_of_par, tc,testset_under_test,s)
                            else:
                                verdict.append((2,'Blocked: the test case is blocked because the test setup failed'))
                                self.logger.debug("The test case %s is blocked for build %s, will skip it." % (tc.FormattedID,self.data["ts"]["Build"]))
                            '''
                            s = requests.session()
                            verdict,variable_value_dict=self.runTC(tc, verdict, testset_under_test,constants.STEPS_SUP_EXE_FLC_VER_CLU,{},s,"")
                            break
                                                        
                else:
                    '''
                    lst=tc.c_QATCPARAMSTEXT.split('|')
                    s = requests.session()
                    setup_result,lst=self.setup(lst, tc, testset_under_test, s)
                    if setup_result==True:
                        (response,lst_of_par)=self.executor(lst,tc,s)
                        verdict=self.firstLevelCheck(lst_of_par, response, verdict, tc,s)
                        if verdict[-1][0]!=0:
                            verdict=self.verificator(lst_of_par, response, verdict, tc,s)
                        self.cleaner(lst_of_par, tc,testset_under_test,s)
                    else:
                        verdict.append((2,'Blocked: the test case is blocked because the test setup failed'))
                        self.logger.debug("The test case %s is blocked for build %s, will skip it." % (tc.FormattedID,self.data["ts"]["Build"]))
                    '''
                    s = requests.session()
                    verdict,variable_value_dict=self.runTC(tc, verdict, testset_under_test,constants.STEPS_SUP_EXE_FLC_VER_CLU,{},s,"")
            
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
            ts=ts_obj.getTSByID(new_data['ts']['FormattedID'])[0]
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
                        if (not hasattr(df.TestCaseResult,'Notes')) or (str(df.TestCaseResult.Notes) != dic['tcresult']['Notes']):
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
                            #check if the defect is marked as fixed or closed
                            if df.State == "Fixed" or df.State == "Closed":
                                update_df={'df':None}
                                #reopen the defect, make notes about the build, env and steps. Assign to someone
                                update_df['df']={"FormattedID":df.FormattedID,"State":"Open","Owner":getattr(df.Owner,'_ref',None),"Notes":df.Notes+"<br>The defect is reproduced in build %s, test set %s, test case %s.<br />" % (new_data['ts']['Build'],ts.FormattedID,tc.FormattedID)}        
                                self.logger.debug("The defect %s is reproduced in build %s, test set %s, test case %s. Will re-open and update it with repro info" % (df.FormattedID,new_data['ts']['Build'],ts.FormattedID,tc.FormattedID))                      
                            else: #inserting notes. 
                                update_df={'df':None}
                                #print df.Notes
                                update_df['df']= {"FormattedID":df.FormattedID,"Notes":df.Notes+"<br>The defect is reproduced in build %s, test set %s, test case %s.<br />" % (new_data['ts']['Build'],ts.FormattedID,tc.FormattedID)}
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
            

