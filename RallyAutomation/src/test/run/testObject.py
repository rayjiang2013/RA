'''
Created on Nov 10, 2014

@author: ljiang
'''


#from testSet import *
from smtplib import *
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import sys
#sys.setrecursionlimit(1500)
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

from jenkinsNotifier import jenkinsNotifier
from dateutil import tz

import json

import constants
import re

from helper import helper

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
        self.helper_obj=helper(rally,data)
    
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
    
    #Get last build information. 
    def getLastBuildInfoFromJenkins(self):
        try:
            jenkins_obj=jenkinsNotifier(self.rally,self.data)
            server=jenkins_obj.getServerInstance()
            build_obj,job_obj=jenkins_obj.getLastBuildInfo(server)
            duration_list=str(build_obj.get_duration()).split(':')
            duration_double=int(duration_list[0])*3600+int(duration_list[1])*60+float(duration_list[2])
            utc1=str(build_obj.get_timestamp()).split('+')[0] #2015-03-19 00:01:35+00:00
            utc2=datetime.datetime.strptime(utc1,'%Y-%m-%d %H:%M:%S')
            from_zone = tz.tzutc()
            to_zone = tz.tzlocal()
            utc2 = utc2.replace(tzinfo=from_zone)
            local = utc2.astimezone(to_zone)
            local_iso=local.isoformat()
            bd_dict={
                     'Number':build_obj.get_number(),
                     'Duration':duration_double,
                     'Uri':build_obj.baseurl, 
                     'Message':'Build for job '+job_obj.name+ ' was successful.',
                     'Status': build_obj.get_status(),
                     'Start':local_iso
                     }
            bddf_dict={
                       'Name':job_obj.name
                       }
            self.data['build'].update(bd_dict)
            self.data['builddf'].update(bddf_dict)
            self.logger.info("The last build information at Jenkins instance %s is successfully obtained" % (server.baseurl))
        except Exception, details:

            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)            
    
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
    
    #Setup
    def setup(self,lst,tc,ts,s_ession,variable_value_dict,verdict,search_path,parrent_tc,steps_type,search_index):
        try:
            verdict_api_list=[]
            tc_api_list=[]
            setup_calls=lst[constants.INDEXES_SUP[0]].split(";")
            if lst[constants.INDEXES_SUP[1]]!=u'':
                lst[constants.INDEXES_SUP[1]]=self.data['env']['ControllerURL']+lst[constants.INDEXES_SUP[1]]            
            
            #verdict=None
            r_stp=None
            if lst[constants.INDEXES_SUP[0]]==u"":
                self.logger.debug("As not enough setup information is provided, the test setup for test case %s build %s  test set %s is skipped" % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))
                verdict.append((constants.SUCCESS,"as not enough setup information is provided, the test setup is skipped"))
            else: 
                # The Get/POST/DELETE/PUT will not be executed as the api call should always be predefined 
                if lst[constants.INDEXES_SUP[0]] == "GET":
                    #The following is to replace all fields at once, which does not fit for the requirements of TA77541
                    rep_status,lst,varbs,missing_varbs,missing_varbs_string=self.helper_obj.repAll(constants.INDEXES_SUP, lst, parrent_tc, variable_value_dict, tc, steps_type, search_path, setup_calls, search_index, verdict)
                    if rep_status==False:
                        self.logger.debug("The test case %s for build %s in test set %s is failed to setup because %s is/are not defined in extra.json or pre-defined local variables." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID,missing_varbs_string))    
                        verdict.append((constants.BLOCKED,"fail to setup as %s is/are not defined in extra.json or pre-defined local variables" % missing_varbs_string))
                        return verdict,lst,variable_value_dict    
                    r_stp = s_ession.get(lst[constants.INDEXES_SUP[1]])                        
                elif lst[constants.INDEXES_SUP[0]] == "POST":
                    #The following is to replace all fields at once, which does not fit for the requirements of TA77541
                    rep_status,lst,varbs,missing_varbs,missing_varbs_string=self.helper_obj.repAll(constants.INDEXES_SUP, lst, parrent_tc, variable_value_dict, tc, steps_type, search_path, setup_calls, search_index, verdict)
                    if rep_status==False:
                        self.logger.debug("The test case %s for build %s in test set %s is failed to setup because %s is/are not defined in extra.json or pre-defined local variables." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID,missing_varbs_string))    
                        verdict.append((constants.BLOCKED,"fail to setup as %s is/are not defined in extra.json or pre-defined local variables" % missing_varbs_string))
                        return verdict,lst,variable_value_dict    
                    r_stp = s_ession.post(lst[constants.INDEXES_SUP[1]],data=json.loads(lst[constants.INDEXES_SUP[2]]))
                elif lst[constants.INDEXES_SUP[0]] == "DELETE":
                    #The following is to replace all fields at once, which does not fit for the requirements of TA77541
                    rep_status,lst,varbs,missing_varbs,missing_varbs_string=self.helper_obj.repAll(constants.INDEXES_SUP, lst, parrent_tc, variable_value_dict, tc, steps_type, search_path, setup_calls, search_index, verdict)
                    if rep_status==False:
                        self.logger.debug("The test case %s for build %s in test set %s is failed to setup because %s is/are not defined in extra.json or pre-defined local variables." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID,missing_varbs_string))    
                        verdict.append((constants.BLOCKED,"fail to setup as %s is/are not defined in extra.json or pre-defined local variables" % missing_varbs_string))
                        return verdict,lst,variable_value_dict    
                    r_stp = s_ession.delete(lst[constants.INDEXES_SUP[1]])
                elif lst[constants.INDEXES_SUP[0]] == "PUT":
                    #The following is to replace all fields at once, which does not fit for the requirements of TA77541
                    rep_status,lst,varbs,missing_varbs,missing_varbs_string=self.helper_obj.repAll(constants.INDEXES_SUP, lst, parrent_tc, variable_value_dict, tc, steps_type, search_path, setup_calls, search_index, verdict)
                    if rep_status==False:
                        self.logger.debug("The test case %s for build %s in test set %s is failed to setup because %s is/are not defined in extra.json or pre-defined local variables." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID,missing_varbs_string))    
                        verdict.append((constants.BLOCKED,"fail to setup as %s is/are not defined in extra.json or pre-defined local variables" % missing_varbs_string))
                        return verdict,lst,variable_value_dict    
                    r_stp = s_ession.put(lst[constants.INDEXES_SUP[1]],data=json.loads(lst[constants.INDEXES_SUP[2]]))
                else:
                    #check if lst[constants.INDEXES_CLU[4]] is api level test case, if it does run api level test case
                    apits_id=self.data['apits']['FormattedID']
                    ts_obj=testSet(self.rally,self.data)
                    ts_api=ts_obj.getTSByID(apits_id)[0]
                    
                    api_list=lst[constants.INDEXES_SUP[0]].split(';')
                    api_json_requst_lst=lst[constants.INDEXES_SUP[2]].split(';')
                    
                    if len(api_list)>len(api_json_requst_lst):
                        append_num=len(api_list)-len(api_json_requst_lst)
                        append_num_indx=0
                        while append_num_indx<append_num:
                            api_json_requst_lst.append('')
                            append_num_indx+=1             
                    #if len(api_list)==len(api_json_requst_lst)+1:
                        #api_json_requst_lst.append('')
                    if len(api_list)<len(api_json_requst_lst):    
                        #raise Exception("The test case %s for build %s is failed to cleanup because there are more number of request content than that of api call" % (tc.FormattedID,self.data["ts"]["Build"]))
                        self.logger.debug("The test case %s for build %s in test set %s is failed to setup because there are more number of request content than that of api call" % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))    
                        verdict.append((constants.BLOCKED,"fail to setup as there are more number of request content than that of api call"))                
                        return verdict,lst,variable_value_dict
                    #if len(api_list)>len(api_json_requst_lst)+1:    
                        #raise Exception("The test case %s for build %s is failed to cleanup because there are more number of request content than that of api call" % (tc.FormattedID,self.data["ts"]["Build"]))
                        #self.logger.debug("The test case %s for build %s in test set %s is failed to setup because there are more number of api calls than that of request content" % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))    
                        #verdict.append((constants.BLOCKED,"fail to setup as there are more number of api calls than that of request content"))                
                        #return verdict,lst,variable_value_dict                    
                         
                    for api_call,api_json_request in zip(api_list,api_json_requst_lst):                        
                        for tc_api in ts_api.TestCases:
                            if tc_api.Name==api_call:
                                '''
                                if '$' in api_json_request:
                                    if parrent_tc!=None:
                                        rep_status,api_json_request,varbs,missing_varbs=self.helper_obj.rep(api_json_request,variable_value_dict,tc.Name,parrent_tc.Name,steps_type,search_path,setup_calls,search_index)
                                    if parrent_tc==None:
                                        rep_status,api_json_request,varbs,missing_varbs=self.helper_obj.rep(api_json_request,variable_value_dict,tc.Name,"",steps_type,search_path,setup_calls,search_index)
                                    if rep_status==False:
                                        missing_varbs_string=missing_varbs[0]
                                        for i in missing_varbs:
                                            if len(missing_varbs)==1:                                    
                                                break
                                            if missing_varbs.index(i)>0:
                                                missing_varbs_string=missing_varbs_string+", "+i
                                        #raise Exception("The test case %s for build %s in test set %s is failed to setup because %s in extra.json is not defined." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID,varbs[-1]))
                                        #if len(missing_varbs)==1:
                                        self.logger.debug("The test case %s for build %s in test set %s is failed to setup because %s is/are not defined in extra.json or pre-defined local variables." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID,missing_varbs_string))    
                                        verdict.append((constants.BLOCKED,"fail to setup as %s is/are not defined in extra.json or pre-defined local variables" % missing_varbs_string))
                                        return verdict,lst,variable_value_dict                                                 
                                '''     
                                rep_status,new_api_json_request,varbs,missing_varbs,missing_varbs_string=self.helper_obj.repOneJSONRequest(api_json_request,variable_value_dict,tc,parrent_tc,steps_type,search_path,setup_calls,search_index)
                                lst[constants.INDEXES_SUP[2]]=lst[constants.INDEXES_SUP[2]].replace(api_json_request,new_api_json_request,1)
                                if rep_status==False:
                                    self.logger.debug("The test case %s for build %s in test set %s is failed to setup because %s is/are not defined in extra.json or pre-defined local variables." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID,missing_varbs_string))    
                                    verdict.append((constants.BLOCKED,"fail to setup as %s is/are not defined in extra.json or pre-defined local variables" % missing_varbs_string))
                                    return verdict,lst,variable_value_dict         
                                verdict_api,variable_value_dict=self.runTC(tc_api, [], ts_api,constants.STEPS_EXE_FLC_VER,variable_value_dict,s_ession,new_api_json_request,tc,search_path,search_index)
                                #variable_value_dict_dict.setdefault(api_call,[]).append(variable_value_dict)
                                verdict_api_list.append(verdict_api)
                                tc_api_list.append(tc_api)
                                break
                        else:
                            self.logger.debug("The test case %s for build %s in test set %s is failed to setup because the api call is unexpected." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))    
                            verdict.append((constants.BLOCKED,"fail to setup as the api call is unexpected"))                
                            return verdict,lst,variable_value_dict 
                        
                if r_stp!=None:
                    if r_stp.status_code != int(lst[constants.INDEXES_SUP[3]]):
                        self.logger.debug("The test case %s for build %s in test set %s is failed to setup because status code is unexpected." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))    
                        verdict.append((constants.BLOCKED,"fail to setup as status code is unexpected")) 
                        return verdict,lst,variable_value_dict          
                    else:
                        if (lst[constants.INDEXES_SUP[4]] != u'' ):
                            ver_point=deepcopy(json.loads(lst[constants.INDEXES_SUP[4]]))
                            r_ver_content=deepcopy(json.loads(r_stp.content))
                            
                            error_message=self.helper_obj.searchDict2(ver_point,r_ver_content,"")
                            if error_message=='':
                                self.logger.debug("The test case %s for build %s in test set %s is setup successfully." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))
                                verdict.append((constants.SUCCESS,"the test case is setup successfully"))
                            else:
                                self.logger.debug("The test case %s for build %s in test set %s is failed to setup because the content of response body is unexpected" % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))   
                                verdict.append((constants.BLOCKED,"fail to setup as the content of response body is unexpected"))
                                return verdict,lst,variable_value_dict
                        else:
                            self.logger.debug("The test case %s for build %s in test set %s is setup successfully." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID)) 
                            verdict.append((constants.SUCCESS,"the test case is setup successfully"))      
                
                if len(verdict_api_list)>0:
                    num=0
                    while num < len(verdict_api_list):
                        if num==0:
                            #if verdict_api_list[num] != None:
                            if verdict_api_list[num][-1][0]!=constants.SUCCESS:
                                self.logger.debug("The test case %s for build %s in test set %s is failed to setup because the restful api level test case %s (%s) failed: %s" % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID,tc_api_list[num].FormattedID,tc_api_list[num].Name,verdict_api_list[num][-1][1]))   
                                verdict.append((constants.BLOCKED,"fail to setup as the restful api level test case %s (%s) failed: %s" % (tc_api_list[num].FormattedID,tc_api_list[num].Name,verdict_api_list[num][-1][1])))
                            else:
                                self.logger.debug("The test case %s for build %s in test set %s is setup successfully." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))    
                                verdict.append((constants.SUCCESS,"the test case is setup successfully"))  
                        else:
                            #if verdict_api_list[num] != None:
                            if verdict_api_list[num][-1][0]!=constants.SUCCESS:
                                self.logger.debug("The test case %s for build %s in test set %s is failed to setup because the restful api level test case %s (%s) failed: %s" % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID,tc_api_list[num].FormattedID,tc_api_list[num].Name,verdict_api_list[num][-1][1]))   
                                verdict[-1]=(constants.BLOCKED,verdict[-1][1]+'; fail to setup as the restful api level test case %s (%s) failed: %s' % (tc_api_list[num].FormattedID,tc_api_list[num].Name,verdict_api_list[num][-1][1]))

                        num+=1
                    return verdict,lst,variable_value_dict 

                else:
                    self.logger.debug("The test case %s for build %s in test set %s is setup successfully." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))    
                    verdict.append((constants.SUCCESS,"the test case is setup successfully"))                   
                '''
                for verdict_api in verdict_api_list:
                    if verdict_api != None:
                        if verdict_api[0][0]!=1:
                            self.logger.debug("The test case %s for build %s in test set %s is failed to setup because the restful api level test case %s (%s) failed: %s" % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID,tc_api.FormattedID,tc_api.Name,verdict_api[0][1]))   
                            verdict.append((constants.BLOCKED,"fail to setup as the restful api level test case %s (%s) failed: %s" % (tc_api.FormattedID,tc_api.Name,verdict_api[0][1])))
                            return verdict,lst,variable_value_dict  
                '''             

                    
            return verdict,lst,variable_value_dict 
        except Exception, details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)       
        
            
    #Test execution
    def executor(self,lst,tc,s_ession,variable_value_dict,request_to_sub,verdict,steps_type,parrent_tc,search_path,search_index):
        try:
            setup_calls=lst[constants.INDEXES_SUP[0]].split(";")
            local_variable_dict={}
            if steps_type==constants.STEPS_SUP_EXE_FLC_VER or steps_type==constants.STEPS_SUP_EXE_FLC_VER_CLU:
                pass 
                #verdict[-1]=(verdict[-1][0],verdict[-1][1]+'; execution is successful')  
            elif steps_type==constants.STEPS_EXE_FLC_VER:
                verdict.append((constants.SUCCESS,""))   
                #verdict.append((constants.SUCCESS,"execution is successful"))   
                    
            if lst[constants.INDEXES_EXE[1]]!= u'':
                lst[constants.INDEXES_EXE[1]]=self.data['env']['ControllerURL']+lst[constants.INDEXES_EXE[1]]            

            if len(request_to_sub)!=0:
                lst[constants.INDEXES_EXE[2]]=request_to_sub
            
            missing_varbs_string=""
            for idx in constants.INDEXES_EXE:
                if '$' in lst[idx]:
                    if parrent_tc!=None:
                        rep_status,lst[idx],varbs,missing_varbs=self.helper_obj.rep(lst[idx],variable_value_dict,tc.Name,parrent_tc.Name,steps_type,search_path,setup_calls,search_index)
                    if parrent_tc==None:
                        rep_status,lst[idx],varbs,missing_varbs=self.helper_obj.rep(lst[idx],variable_value_dict,tc.Name,"",steps_type,search_path,setup_calls,search_index)
                    if rep_status==False:
                        missing_varbs_string=missing_varbs[0]
                        for i in missing_varbs:
                            if len(missing_varbs)==1:                                    
                                break
                            if missing_varbs.index(i)>0:
                                missing_varbs_string=missing_varbs_string+", "+i
                        #raise Exception("The test case %s for build %s is failed to execute because %s in extra.json is not defined." % (tc.FormattedID,self.data["ts"]["Build"],varbs[-1]))
                        self.logger.debug("The test case %s for build %s is blocked because %s is/are not defined in extra.json or pre-defined local variables." % (tc.FormattedID,self.data["ts"]["Build"],missing_varbs_string))    
                        #if len(verdict)==0:
                        if steps_type==constants.STEPS_SUP_EXE_FLC_VER or steps_type==constants.STEPS_SUP_EXE_FLC_VER_CLU:
                            verdict[-1]=(constants.BLOCKED,verdict[-1][1]+"; fail to execute as %s is/are not defined in extra.json or pre-defined local variables" % missing_varbs_string)
                        if steps_type==constants.STEPS_EXE_FLC_VER:
                            verdict[-1]=(constants.BLOCKED,"fail to execute as %s is/are not defined in extra.json or pre-defined local variables" % missing_varbs_string)
                            #verdict.append((constants.BLOCKED,"Blocked: fail to execute as %s is/are not defined in extra.json or pre-defined local variables" % missing_varbs_string))
                        return verdict,lst,variable_value_dict,None,False,search_path  
           
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
                        self.logger.debug("The test case %s for build %s is blocked because JSON object to make POST request is missing" % (tc.FormattedID,self.data["ts"]["Build"]))
                        if steps_type==constants.STEPS_SUP_EXE_FLC_VER or steps_type==constants.STEPS_SUP_EXE_FLC_VER_CLU:
                            verdict[-1]=(constants.BLOCKED,verdict[-1][1]+"; fail to execute as JSON object to make POST request is missing")
                        if steps_type==constants.STEPS_EXE_FLC_VER:
                            verdict[-1]=(constants.BLOCKED,"fail to execute as JSON object to make POST request is missing")
                            #verdict.append((constants.BLOCKED,"Blocked: fail to execute as JSON object to make POST request is missing"))
                        return verdict,lst,variable_value_dict,None,False,search_path 
                elif lst[constants.INDEXES_EXE[0]] == "DELETE":
                    r = s_ession.delete(lst[constants.INDEXES_EXE[1]])
                elif lst[constants.INDEXES_EXE[0]] == "PUT":#only support http for now, verify = false
                    if lst[constants.INDEXES_EXE[2]]!='':
                        json_request=json.loads(lst[constants.INDEXES_EXE[2]])                
                        r = s_ession.put(lst[constants.INDEXES_EXE[1]],data=json_request,verify=False)
                    else:
                        self.logger.debug("The test case %s for build %s is blocked because JSON object to make PUT request is missing" % (tc.FormattedID,self.data["ts"]["Build"]))
                        if steps_type==constants.STEPS_SUP_EXE_FLC_VER or steps_type==constants.STEPS_SUP_EXE_FLC_VER_CLU:
                            verdict[-1]=(constants.BLOCKED,verdict[-1][1]+"; fail to execute as JSON object to make PUT request is missing")
                        if steps_type==constants.STEPS_EXE_FLC_VER:
                            verdict[-1]=(constants.BLOCKED,"fail to execute as JSON object to make PUT request is missing")
                            #verdict.append((constants.BLOCKED,"Blocked: fail to execute as JSON object to make PUT request is missing"))
                        return verdict,lst,variable_value_dict,None,False,search_path                   
                else:
                    #raise Exception("Unexpected execution method: %s" % lst[constants.INDEXES_EXE[0]])
                    if lst[constants.INDEXES_EXE[0]]=="":
                        self.logger.debug("No execution method is provided")  
                        if steps_type==constants.STEPS_SUP_EXE_FLC_VER or steps_type==constants.STEPS_SUP_EXE_FLC_VER_CLU:
                            verdict[-1]=(constants.BLOCKED,verdict[-1][1]+"; fail to execute as no execution method is provided")
                        if steps_type==constants.STEPS_EXE_FLC_VER:
                            verdict[-1]=(constants.BLOCKED,"fail to execute as no execution method is provided")
                            #verdict.append((constants.BLOCKED,"Blocked: fail to execute as no execution method is provided"))                        
                    else:
                        self.logger.debug("Unexpected execution method: %s" % lst[constants.INDEXES_EXE[0]])    
                        if steps_type==constants.STEPS_SUP_EXE_FLC_VER or steps_type==constants.STEPS_SUP_EXE_FLC_VER_CLU:
                            verdict[-1]=(constants.BLOCKED,verdict[-1][1]+"; fail to execute as unexpected execution method: %s" % lst[constants.INDEXES_EXE[0]])
                        if steps_type==constants.STEPS_EXE_FLC_VER:
                            verdict[-1]=(constants.BLOCKED,"fail to execute as unexpected execution method: %s" % lst[constants.INDEXES_EXE[0]])
                            #verdict.append((constants.BLOCKED,"Blocked: fail to execute as unexpected execution method: %s" % lst[constants.INDEXES_EXE[0]]))
                    return verdict,lst,variable_value_dict,None,False,search_path  
            else:
                self.logger.debug("No path is provided")    
                if steps_type==constants.STEPS_SUP_EXE_FLC_VER or steps_type==constants.STEPS_SUP_EXE_FLC_VER_CLU:
                    verdict[-1]=(constants.BLOCKED,verdict[-1][1]+"; fail to execute as no path is provided")
                if steps_type==constants.STEPS_EXE_FLC_VER:
                    verdict[-1]=(constants.BLOCKED,"fail to execute as no path is provided")
                    #verdict.append((constants.BLOCKED,"Blocked: fail to execute as no path is provided"))
                return verdict,lst,variable_value_dict,None,False,search_path  

            #variables to save     
                               
            if r.content!="":
                r_ver_content=deepcopy(json.loads(r.content))
    
                if lst[constants.INDEXES_FLC[2]]!="":
                    variable_list=lst[constants.INDEXES_FLC[2]].split(';')
                    #variable_value_dict={}
                    j=0
                    for varb in variable_list:

                        if re.match(r'\w+\=\w+\(\/.*',varb):
                            search_path_in_response=re.match(r'\w+\=\w+\(\/(.*)\)', varb).group(1) 
                            varb_to_pass=re.match(r'(\w+)\=\w+\(\/.*\)', varb).group(1)
                            varb=re.match(r'\w+\=(\w+)\(\/.*\)', varb).group(1) 
                            
                            search_path_in_response_list=search_path_in_response.split("/")   
                            index_dict=json.loads(lst[constants.INDEXES_FLC[3]])
                            if lst[constants.INDEXES_FLC[3]] !="" and type(index_dict) is dict:
                                
                                match_count=0
                                for index,search_path_in_response_list_item in enumerate(search_path_in_response_list):
                                    if re.match(r'\$\w+',search_path_in_response_list_item):
                                        search_path_in_response_list_item_index=re.match(r'\$(\w+)',search_path_in_response_list_item).group(1)
                                        if search_path_in_response_list_item_index in index_dict:
                                            search_path_in_response_list_item_index=index_dict[search_path_in_response_list_item_index]
                                            search_path_in_response_list[index]=search_path_in_response_list_item_index
                                            match_count+=1
                                        else:
                                            self.logger.debug("No index value range provided for %s" % search_path_in_response_list_item_index)  
                                            if steps_type==constants.STEPS_SUP_EXE_FLC_VER or steps_type==constants.STEPS_SUP_EXE_FLC_VER_CLU:
                                                verdict[-1]=(constants.FAILED,verdict[-1][1]+"; fail to execute as no index value range provided for %s" % search_path_in_response_list_item_index)
                                            if steps_type==constants.STEPS_EXE_FLC_VER:
                                                verdict[-1]=(constants.FAILED,'fail to execute as no index value range provided for %s' % search_path_in_response_list_item_index)
                                            break                                             
                                            
                                else:
                                    if match_count<len(index_dict):
                                        self.logger.debug("More index provided than needed")  
                                           
                            elif lst[constants.INDEXES_FLC[3]]=="":
                                self.logger.debug("No index value range provided")  
                                if steps_type==constants.STEPS_SUP_EXE_FLC_VER or steps_type==constants.STEPS_SUP_EXE_FLC_VER_CLU:
                                    verdict[-1]=(constants.FAILED,verdict[-1][1]+"; fail to execute as no index value range provided")
                                if steps_type==constants.STEPS_EXE_FLC_VER:
                                    verdict[-1]=(constants.FAILED,'fail to execute as no index value range provided')
                                break
                            elif type(index_dict)!=dict:
                                self.logger.debug("The format of index value is incorrect")  
                                if steps_type==constants.STEPS_SUP_EXE_FLC_VER or steps_type==constants.STEPS_SUP_EXE_FLC_VER_CLU:
                                    verdict[-1]=(constants.FAILED,verdict[-1][1]+"; fail to execute as the format of index value is incorrect")
                                if steps_type==constants.STEPS_EXE_FLC_VER:
                                    verdict[-1]=(constants.FAILED,'fail to execute as the format of index value is incorrect')     
                                break                
                        else: 
                            search_path_in_response=""
                            search_path_in_response_list=[]
                            varb_to_pass=varb
                        
                        if search_path_in_response=="":
                            values=self.helper_obj.searchKeyInDicNoSearchPath(r_ver_content, varb)    
                        else:
                            values=self.helper_obj.searchKeyInDic(r_ver_content, varb,search_path_in_response_list)
                        i=0
                        
                        if len(values)==0:
                            #if len(verdict)!=0:
                            if steps_type==constants.STEPS_SUP_EXE_FLC_VER or steps_type==constants.STEPS_SUP_EXE_FLC_VER_CLU:
                                if j==0:
                                    verdict[-1]=(constants.FAILED,verdict[-1][1]+'; fail to execute as unable to save values in response content to variables as the variable: %s cannot be found in the response content' % varb)
                                else:
                                    verdict[-1]=(constants.FAILED,verdict[-1][1]+', %s cannot be found in the response content' % varb)
                                
                            if steps_type==constants.STEPS_EXE_FLC_VER:
                                if j==0:
                                    verdict[-1]=(constants.FAILED,'fail to execute as unable to save values in response content to variables as the variable: %s cannot be found in the response content' % varb)
                                    #verdict.append((constants.FAILED,'Failed: fail to execute as unable to save values in response content to variables as the variable: %s cannot be found in the response content' % varb))
                                else:
                                    verdict[-1]=(constants.FAILED,verdict[-1][1]+', %s cannot be found in the response content' % varb)
                                    #verdict.append((constants.FAILED,verdict[-1][1]+', %s cannot be found in the response content' % varb))
                            self.logger.debug("Failed to save values in response content to variable %s as it cannot be found in response content" % varb)     
                                                 
                        elif len(values)>1:
                            while i < len(values):
                                if values[i]!=values[i+1]:
                                    if i ==0:
                                        if steps_type==constants.STEPS_SUP_EXE_FLC_VER or steps_type==constants.STEPS_SUP_EXE_FLC_VER_CLU:
                                            verdict[-1]=(constants.FAILED,verdict[-1][1]+'; fail to execute as unable to save values in response content to variables as there are multiple different values for variable: %s' % varb)
                                        if steps_type==constants.STEPS_EXE_FLC_VER:
                                            verdict[-1]=(constants.FAILED,'fail to execute as unable to save values in response content to variables as there are multiple different values for variable: %s' % varb)
                                            
                                        #verdict.append((constants.FAILED,'Failed: fail to execute as unable to save values in response content to variables as there are multiple different values for variable: %s' % varb))
                                    else:
                                        verdict[-1]=(constants.FAILED,verdict[-1][1]+', %s' % varb)
                                    self.logger.debug("Failed to save values in response content to variable %s as there are multiple different values for it in response" % varb)  
                                    #break                             
                                i+=1
                        else:
                            local_variable_dict[varb_to_pass]=values[0] 
                            self.logger.debug("Successfully save values in response content to variable: %s" % varb)  
                        j+=1
                    #variable_value_dict.setdefault(tc.Name,[]).append(local_variable_dict)
            else:
                r_ver_content=""
            
            #save values in json request into variables
            if len(json_request)!=0:
                variable_list=[]
                if lst[constants.INDEXES_EXE[3]]!="":
                    variable_list=lst[constants.INDEXES_EXE[3]].split(';')
                    j=0
                    for varb in variable_list:
                        values=self.helper_obj.searchKeyInDicNoSearchPath(json_request, varb)
                        i=0
                        
                        if len(values)==0:
                            self.logger.debug("Failed to save values in requested json object to variable %s as it cannot be found in the requested json object" % varb)   
                            if steps_type==constants.STEPS_SUP_EXE_FLC_VER or steps_type==constants.STEPS_SUP_EXE_FLC_VER_CLU:
                                if j==0:
                                    verdict[-1]=(constants.FAILED,verdict[-1][1]+"; fail to execute as unable to save values in requested json object to variables as %s cannot be found in the requested json object" % varb)
                                else:
                                    verdict[-1]=(constants.FAILED,verdict[-1][1]+', %s cannot be found in the requested json object' % varb)
                            if steps_type==constants.STEPS_EXE_FLC_VER:
                                if j==0:
                                    verdict[-1]=(constants.FAILED,"fail to execute as unable to save values in requested json object to variables as %s cannot be found in the requested json object" % varb)
                                else:
                                    verdict[-1]=(constants.FAILED,verdict[-1][1]+', %s cannot be found in the requested json object' % varb)
                            j+=1
                                #verdict.append((constants.FAILED,"Failed: fail to execute as unable to save values in requested json object to variable %s as it cannot be found in the requested json object" % varb))
                            #return verdict,lst,variable_value_dict,r_ver_content,r                   
                        elif len(values)>1:
                            while i < len(values):
                                if values[i]!=values[i+1]:                            
                                    self.logger.debug("Failed to save values in requested json object to variable %s as there are multiple different values for it in the requested json object" % varb)                                      
                                    if i==0:
                                        if steps_type==constants.STEPS_SUP_EXE_FLC_VER or steps_type==constants.STEPS_SUP_EXE_FLC_VER_CLU:
                                            verdict[-1]=(constants.FAILED,verdict[-1][1]+"; fail to execute as unable to save values in requested json object to variables as there are multiple different values for %s" % varb)
                                        if steps_type==constants.STEPS_EXE_FLC_VER:
                                            verdict[-1]=(constants.FAILED,"fail to execute as unable to save values in requested json object to variables as there are multiple different values for %s" % varb)
                                    else:
                                        verdict[-1]=(constants.FAILED,verdict[-1][1]+', %s' % varb)
                                        #verdict.append((constants.FAILED,"Failed: fail to execute as unable to save values in response content to variable %s as there are multiple different values for it in response" % varb))
                                    #return verdict,lst,variable_value_dict,r_ver_content,r                             
                                i+=1
                        else:
                            local_variable_dict[varb]=values[0] 
                            self.logger.debug("Successfully save values in requested json object to variable: %s" % varb)  
                        
            
            #variable_value_dict.setdefault(parrent_tc.Name,[]).append({})

            #check_dict={}
            if search_path=='':
                search_path_list=[]
            else:
                search_path_list=search_path.split("/")  
            variable_value_dict=self.helper_obj.append_local_variable_dict_to_variable_value_dict(search_path_list,variable_value_dict,local_variable_dict,tc.Name)
            
            #variable_value_dict[parrent_tc.Name].setdefault(tc.Name,[]).append(local_variable_dict)
            #variable_value_dict[parrent_tc.Name][tc.Name]=self.remove_number_key_of_dict(self.list_to_dict(variable_value_dict[parrent_tc.Name][tc.Name])) 
            if search_path!=tc.Name:
                search_path=search_path+"/"+tc.Name
            search_path_list=search_path.split("/")            
            
            self.logger.debug("The test case %s for build %s is executed." % (tc.FormattedID,self.data["ts"]["Build"]))     
            
            if verdict[-1][0]==constants.SUCCESS:
                if steps_type==constants.STEPS_SUP_EXE_FLC_VER or steps_type==constants.STEPS_SUP_EXE_FLC_VER_CLU:
                    verdict[-1]=(verdict[-1][0],verdict[-1][1]+'; execution is successful') 
                    #verdict[-1]=(verdict[-1][0],verdict[-1][1]+'; execution is successful')  
                elif steps_type==constants.STEPS_EXE_FLC_VER:
                    verdict[-1]=(verdict[-1][0],'execution is successful') 
                  
                self.logger.debug("The test case %s for build %s is successfully executed." % (tc.FormattedID,self.data["ts"]["Build"]))     
               
            return (verdict,lst,variable_value_dict,r_ver_content,r,search_path) 
        except Exception, details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                print Exception,details
                raise
            else:
                print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1) 

            
    #First level check
    def firstLevelCheck(self,lst,r,verdict,tc,s_ession,variable_value_dict,r_ver_content,parrent_tc,steps_type,search_path,search_index):
        try: 
            setup_calls=lst[constants.INDEXES_SUP[0]].split(";")
            '''
            r_ver_content=deepcopy(json.loads(r.content))
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
            '''
            #ver_point = ast.literal_eval(lst[constants.INDEXES_FLC[0]])

            #r1= r_ver_content.replace("true","\"true\"")
            #r2= r1.replace("false","\"false\"")    
            #r_ver_content=ast.literal_eval(r2)            
            missing_varbs_string=""
            for idx in constants.INDEXES_FLC[0:2]:
                if '$' in lst[idx]:
                    if parrent_tc!=None:
                        rep_status,lst[idx],varbs,missing_varbs=self.helper_obj.rep(lst[idx],variable_value_dict,tc.Name,parrent_tc.Name,steps_type,search_path,setup_calls,search_index)
                    if parrent_tc==None:
                        rep_status,lst[idx],varbs,missing_varbs=self.helper_obj.rep(lst[idx],variable_value_dict,tc.Name,"",steps_type,search_path,setup_calls,search_index)
                    if rep_status==False:
                        missing_varbs_string=missing_varbs[0]
                        for i in missing_varbs:
                            if len(missing_varbs)==1:                                    
                                break
                            if missing_varbs.index(i)>0:
                                missing_varbs_string=missing_varbs_string+", "+i
                        #raise Exception("The test case %s for build %s is failed to pass first level check because %s in extra.json is not defined." % (tc.FormattedID,self.data["ts"]["Build"],varbs[-1]))
                        verdict[-1]=(constants.BLOCKED,verdict[-1][1]+'; %s is/are not defined in extra.json or pre-defined local variables' % missing_varbs_string)
                        self.logger.debug("The test case %s for build %s is failed to pass first level check because %s is/are not defined in extra.json or pre-defined local variables." % (tc.FormattedID,self.data["ts"]["Build"],missing_varbs_string))    
                        #return verdict,variable_value_dict  
                        
                        
            if not(lst[constants.INDEXES_FLC[0]].isdigit()):
                verdict[-1]=(constants.BLOCKED,verdict[-1][1]+'; status code is expected to be digits instead of something else: %s' % lst[constants.INDEXES_FLC[0]])
                self.logger.debug("The test case %s for build %s failed to pass first level check because status code is expected to be digits instead of something else: %s" % (tc.FormattedID,self.data["ts"]["Build"],lst[constants.INDEXES_FLC[0]]))    
                #return verdict,variable_value_dict                  
            
            elif (lst[constants.INDEXES_FLC[0]].isdigit()) and r.status_code != int(lst[constants.INDEXES_FLC[0]]):
                #Run Env Sanity Check
                #to_obj=testObject(self.rally,self.data)       
                if self.sanityCheck():
                    verdict[-1]=(constants.FAILED,verdict[-1][1]+'; status code unexpected. The unexpected status code of the response is %s' % r.status_code) 
                    self.logger.debug("Test case %s, build %s failed because status code unexpected. The unexpected status code of the response is %s" % (tc.FormattedID,self.data["ts"]["Build"],r.status_code))                       
                    #return verdict
                else:    
                    raise Exception('Environment sanity check failed')
                    #verdict.append((0,'Failure: sanity check of environment failed'))            
            else:
                
                if (lst[constants.INDEXES_FLC[1]] != u'' ):# and (r.content==str(lst[constants.INDEXES_FLC[0]])):
                    ver_points=lst[constants.INDEXES_FLC[1]].split(";")
                    error_message_list=[]
                    counter=0
                    for ver_point in ver_points:       
                        ver_point=deepcopy(json.loads(ver_point))
                        if type(r_ver_content)==list:
                            r_ver_content=self.helper_obj.list_to_dict(r_ver_content)
                            r_ver_content=self.helper_obj.remove_number_key_of_dict(r_ver_content)
                        error_message=self.helper_obj.searchDict3(ver_point,r_ver_content,"")
                        error_message_list.append(error_message)
                        if counter==len(ver_points)-1:
                            counter_err=0
                            counter_success=0
                            for e in error_message_list:                                
                                if e !="" and counter_err==0:
                                    verdict[-1]=(constants.FAILED,verdict[-1][1]+'; status code expected but first level check failed. Error:%s' % error_message)
                                    self.logger.debug("Test case %s, build %s failed because first level check failed. Error: %s" % (tc.FormattedID,self.data["ts"]["Build"],error_message))
                                elif e!="" and counter_err<=len(error_message_list)-1:
                                    verdict[-1]=(constants.FAILED,verdict[-1][1]+'; %s' % error_message)
                                    self.logger.debug("Test case %s, build %s failed because first level check failed. Error: %s" % (tc.FormattedID,self.data["ts"]["Build"],error_message))
                                elif e=="":    
                                    counter_success+=1
                                    if counter_err==len(error_message_list)-1 and counter_success==len(error_message_list):
                                        verdict[-1]=(constants.SUCCESS,verdict[-1][1]+'; status code expected and first level check succeed')
                                        self.logger.debug("First level check for Test case %s, build %s is successful." % (tc.FormattedID,self.data["ts"]["Build"]))
                                counter_err+=1
                        '''        
                        if len(ver_points)==1:
                            if error_message=='':
                                #First level check succeed
                                #z=ast.literal_eval(lst[constants.INDEXES_FLC[0]])
                                if 'message' in r.content:
                                    verdict[-1]=(constants.SUCCESS,verdict[-1][1]+'; status code expected and first level check succeed. Message: '+ver_point['message'])
                                else:
                                    verdict[-1]=(constants.SUCCESS,verdict[-1][1]+'; status code expected and first level check succeed')
                                self.logger.debug("First level check for Test case %s, build %s is successful." % (tc.FormattedID,self.data["ts"]["Build"]))
                                break
                            else:
                                #First level check failed
                                verdict[-1]=(constants.FAILED,verdict[-1][1]+'; status code expected but first level check failed. Error:%s' % error_message)
                                self.logger.debug("Test case %s, build %s failed because first level check failed. Error: %s" % (tc.FormattedID,self.data["ts"]["Build"],error_message))
                                break 
                        '''  
                        counter+=1

                else:
                    verdict[-1]=(constants.SUCCESS,verdict[-1][1]+'; status code expected without first level check')
                    self.logger.debug("Test case %s, build %s is successful without first level check." % (tc.FormattedID,self.data["ts"]["Build"]))
                     
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
    def verificator(self,lst,r,verdict,tc,s_ession,variable_value_dict,search_path,parrent_tc,steps_type,search_index):
        try:
            setup_calls=lst[constants.INDEXES_SUP[0]].split(";")
            if lst[constants.INDEXES_VER[1]]!= u'':
                lst[constants.INDEXES_VER[1]]=self.data['env']['ControllerURL']+lst[constants.INDEXES_VER[1]]
            
            missing_varbs_string=""
            for idx in constants.INDEXES_VER:
                if '$' in lst[idx]:
                    if parrent_tc!=None:
                        rep_status,lst[idx],varbs,missing_varbs=self.helper_obj.rep(lst[idx],variable_value_dict,tc.Name,parrent_tc.Name,steps_type,search_path,setup_calls,search_index)
                    if parrent_tc==None:
                        rep_status,lst[idx],varbs,missing_varbs=self.helper_obj.rep(lst[idx],variable_value_dict,tc.Name,"",steps_type,search_path,setup_calls,search_index)
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
                verdict[-1]=(verdict[-1][0],verdict[-1][1]+'; no verification is done.')
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
                    
                    error_message=self.helper_obj.searchDict2(ver_point,r_ver_content,"")
                    if error_message=='':
                        verdict[-1]=(verdict[-1][0],verdict[-1][1]+'; verification is successful.')
                        #verdict.append((1,'Success: status code expected and verified'))
                        self.logger.debug("The test execution for test case %s, build %s is verified to be successful." % (tc.FormattedID,self.data["ts"]["Build"]))                  
                    else:
                        verdict[-1]=(constants.FAILED,verdict[-1][1]+'; verification failed, error: %s' % error_message)
                        self.logger.debug("The test execution for test case %s, build %s is verified to be failed. Error: %s" % (tc.FormattedID,self.data["ts"]["Build"],error_message))   
                        
                else:
                    #check if lst[constants.INDEXES_VER[1]] is api level test case, if it does run api level test case
                    apits_id=self.data['apits']['FormattedID']
                    ts_obj=testSet(self.rally,self.data)
                    ts_api=ts_obj.getTSByID(apits_id)[0]
                    
                    verdict_api=None
                    for tc_api in ts_api.TestCases:
                        if tc_api.Name==lst[constants.INDEXES_VER[2]]:
                            verdict_api,variable_value_dict=self.runTC(tc_api, [], ts_api,constants.STEPS_EXE_FLC_VER,variable_value_dict,s_ession,lst[constants.INDEXES_VER[3]],tc,search_path,search_index)
                            break
                    
                    if verdict_api!=None:
                        if verdict_api[0][0]==1:
                            verdict[-1]=(verdict[-1][0],verdict[-1][1]+'; verification is successful.')
                            self.logger.debug("The test execution of test case %s for build %s is verified to be successfully." % (tc.FormattedID,self.data["ts"]["Build"]))       
                        else:
                            verdict[-1]=(constants.FAILED,verdict[-1][1]+'; verification failed, error: the api level test case %s failed: %s' % (tc_api.Name,verdict_api[0][1]))
                            self.logger.debug("The test case %s for build %s is failed to verify because the api level test case %s (%s) failed: %s" % (tc.FormattedID,self.data["ts"]["Build"],tc_api.FormattedID,tc_api.Name,verdict_api[0][1]))   
                            #return False,lst                
                    else:
                        verdict[-1]=(constants.FAILED,verdict[-1][1]+'; verification failed, error: the api level test case name %s cannot be found in API test set %s' % (lst[constants.INDEXES_VER[2]],apits_id))
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
    def cleaner(self,lst,tc,ts,s_ession,variable_value_dict,search_path,parrent_tc,steps_type,search_index):
        try:                       
            setup_calls=lst[constants.INDEXES_SUP[0]].split(";")
            if lst[constants.INDEXES_CLU[1]]!= u'':
                lst[constants.INDEXES_CLU[1]]=self.data['env']['ControllerURL']+lst[constants.INDEXES_CLU[1]]
                                        
            r_clr=None
            if lst[constants.INDEXES_CLU[0]]==u"":
                self.logger.debug("As not enough cleanup information is provided, the test cleanup for test case %s, build %s, test set %s is skipped" % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))
            else: 
                missing_varbs_string=""    
                for idx in constants.INDEXES_CLU:
                    if '$' in lst[idx]:
                        if parrent_tc!=None:
                            rep_status,lst[idx],varbs,missing_varbs=self.helper_obj.rep(lst[idx],variable_value_dict,tc.Name,parrent_tc.Name,steps_type,search_path,setup_calls,search_index)
                        if parrent_tc==None:
                            rep_status,lst[idx],varbs,missing_varbs=self.helper_obj.rep(lst[idx],variable_value_dict,tc.Name,"",steps_type,search_path,setup_calls,search_index)
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

                if lst[constants.INDEXES_CLU[0]] == "GET":
                    r_clr = s_ession.get(lst[constants.INDEXES_CLU[1]])                        
                elif lst[constants.INDEXES_CLU[0]] == "POST":
                    r_clr = s_ession.post(lst[constants.INDEXES_CLU[1]],data=json.loads(lst[constants.INDEXES_CLU[2]]))
                elif lst[constants.INDEXES_CLU[0]] == "DELETE":
                    r_clr = s_ession.delete(lst[constants.INDEXES_CLU[1]])
                elif lst[constants.INDEXES_CLU[0]] == "PUT":
                    r_clr = s_ession.put(lst[constants.INDEXES_CLU[1]],data=json.loads(lst[constants.INDEXES_CLU[2]]))

                else:        
                    #check if lst[constants.INDEXES_CLU[0]] is api level test case, if it does run api level test case
                    apits_id=self.data['apits']['FormattedID']
                    ts_obj=testSet(self.rally,self.data)
                    ts_api=ts_obj.getTSByID(apits_id)[0]
                    
                    verdict_api=None
                    api_tc_lst=lst[constants.INDEXES_CLU[0]].split(';')
                    api_json_requst_lst=lst[constants.INDEXES_CLU[2]].split(';')
                    
                    if len(api_tc_lst)>len(api_json_requst_lst):
                        append_num=len(api_tc_lst)-len(api_json_requst_lst)
                        append_num_indx=0
                        while append_num_indx<append_num:
                            api_json_requst_lst.append('')
                            append_num_indx+=1             
                    #if len(api_tc_lst)==len(api_json_requst_lst)+1:
                        #api_json_requst_lst.append('')
                    if len(api_tc_lst)<len(api_json_requst_lst):    
                        raise Exception("The test case %s for build %s is failed to cleanup because there are more number of request content than that of api call" % (tc.FormattedID,self.data["ts"]["Build"]))
                    #if len(api_tc_lst)>len(api_json_requst_lst)+1:    
                        #raise Exception("The test case %s for build %s is failed to cleanup because there are more number of api calls than that of request content" % (tc.FormattedID,self.data["ts"]["Build"]))
                        #self.logger.debug("The test case %s for build %s in test set %s is failed to setup because there are more number of api calls than that of request content" % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))    
                        #verdict.append((constants.BLOCKED,"fail to setup as there are more number of api calls than that of request content"))                
                        #return verdict,lst,variable_value_dict                      
                    c=0
                    for api_tc,api_json_request in zip(api_tc_lst,api_json_requst_lst):   
                        #check if the api call has search path as parameter
                        if re.match(r'\w+\(\/\w+',api_tc):
                            if re.match(r'\w+\(\/\w+\[\d+\]', api_tc):
                                search_path_append=re.match(r'\w+\((\/\w+)\[\d+\]', api_tc).group(1)
                                if c==0:
                                    search_path=search_path+search_path_append
                                    c+=1
                                search_index=re.match(r'\w+\(\/\w+\[(\d+)\]', api_tc).group(1)
                                api_tc=re.match(r'(\w+)\(\/\w+\[\d+\]', api_tc).group(1) 
                            else:
                                search_path_append=re.match(r'\w+\((\/\w+)\)', api_tc).group(1)
                                if c==0:
                                    search_path=search_path+search_path_append
                                    c+=1
                                api_tc=re.match(r'(\w+)\(\/\w+\)', api_tc).group(1)     
                                search_index=None                
                        for tc_api in ts_api.TestCases:
                            if tc_api.Name==api_tc:
                                verdict_api,variable_value_dict=self.runTC(tc_api, [], ts_api,constants.STEPS_EXE_FLC_VER,variable_value_dict,s_ession,api_json_request,tc,search_path,search_index)
                                if verdict_api!=None:
                                    if verdict_api[0][0]==constants.SUCCESS:
                                        #verdict[-1]=(verdict[-1][0],verdict[-1][1]+' Verification is successful.')
                                        self.logger.debug("The test cleanup of test case %s for build %s is successfully." % (tc.FormattedID,self.data["ts"]["Build"]))       
                                    else:
                                        #verdict[-1]=(constants.FAILED,'Failure: verification failed. Error: the api level test case %s is %s' % (tc_api.Name,verdict_api[0][1]))
                                        raise Exception("The test case %s for build %s is failed to cleanup because the api level test case %s (%s) failed: %s" % (tc.FormattedID,self.data["ts"]["Build"],tc_api.FormattedID,tc_api.Name,verdict_api[0][1]))   
                                        #return False,lst                                    
                                break         
                        else:
                            #verdict[-1]=(constants.FAILED,'Failure: verification failed. Error: the api level test case name %s cannot be found in API test set %s' % (lst[constants.INDEXES_VER[2]],apits_id))
                            raise Exception("The test case %s for build %s is failed to clean up because the api level test case name %s cannot be found in API test set %s" % (tc.FormattedID,self.data["ts"]["Build"],api_tc,apits_id))   

                if r_clr!=None:
                    if r_clr.status_code != int(lst[constants.INDEXES_CLU[3]]):
                        raise Exception("The test case %s for build %s in test set %s is failed to clean up." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))                
                    else:
                        if (lst[constants.INDEXES_CLU[4]] != u'' ):
                            ver_point=deepcopy(json.loads(lst[constants.INDEXES_CLU[4]]))
                            r_ver_content=deepcopy(json.loads(r_clr.content))
                            
                            error_message=self.helper_obj.searchDict2(ver_point,r_ver_content,"")
                            if error_message=='':
                                self.logger.debug("The test case %s for build %s in test set %s is cleaned up successfully." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))
                            else:
                                raise Exception("The test case %s for build %s in test set %s is failed to clean up." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))                    
                        else:
                            self.logger.debug("The test case %s for build %s in test set %s is cleaned up successfully." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))       
                             
        except Exception, details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
    
    #run a single test case
    def runTC(self,tc,verdict,testset_under_test,steps_type,variable_value_dict,s,request_to_sub,parrent_tc,search_path,search_index):
        if steps_type==constants.STEPS_SUP_EXE_FLC_VER_CLU: #1 means run through all steps
            lst=tc.c_QATCPARAMSTEXT.split('|')
            #s = requests.session()
            verdict,lst,variable_value_dict=self.setup(lst, tc, testset_under_test, s,variable_value_dict,verdict,search_path,parrent_tc,steps_type,search_index)
            if verdict[-1][0]==constants.SUCCESS:
                (verdict,lst_of_par,variable_value_dict,r_ver_content,response,search_path)=self.executor(lst,tc,s,variable_value_dict,request_to_sub,verdict,steps_type,parrent_tc,search_path,search_index)
                '''
                if verdict[-1][0]==constants.FAILED:
                    #verdict.append((constants.FAILED,'Failed: the test case failed because execution step failed'))
                    self.logger.debug("The test case %s failed for build %s in execution step, will do test cleanup directly." % (tc.FormattedID,self.data["ts"]["Build"]))
                    self.cleaner(lst_of_par, tc,testset_under_test,s,variable_value_dict)
                '''
                if verdict[-1][0]==constants.BLOCKED:
                    #verdict.append((constants.BLOCKED,'Blocked: the test case is blocked because the restful api call failed to run'))
                    self.logger.debug("The test case %s is blocked for build %s, will skip it." % (tc.FormattedID,self.data["ts"]["Build"]))                                        
                #elif verdict[-1][0]==constants.SUCCESS:
                else:
                    verdict,variable_value_dict=self.firstLevelCheck(lst_of_par, response, verdict, tc,s,variable_value_dict,r_ver_content,parrent_tc,steps_type,search_path,search_index)
                    if verdict[-1][0]==constants.SUCCESS:
                        verdict=self.verificator(lst_of_par, response, verdict, tc,s,variable_value_dict,search_path,parrent_tc,steps_type,search_index)
                    self.cleaner(lst_of_par, tc,testset_under_test,s,variable_value_dict,search_path,parrent_tc,steps_type,search_index)
            else:
                #verdict.append((constants.BLOCKED,'Blocked: the test case is blocked because the test setup failed'))
                self.logger.debug("The test case %s is blocked for build %s, will skip it." % (tc.FormattedID,self.data["ts"]["Build"]))
            return verdict,variable_value_dict                        
       
        if steps_type==constants.STEPS_SUP_EXE_FLC_VER: #run only setup, execution, firstlevelcheck and verification
            lst=tc.c_QATCPARAMSTEXT.split('|')
            #s = requests.session()
            verdict,lst,variable_value_dict=self.setup(lst, tc, testset_under_test, s,variable_value_dict,verdict,search_path,parrent_tc,steps_type,search_index)
            if verdict[-1][0]==constants.SUCCESS:
                (verdict,lst_of_par,variable_value_dict,r_ver_content,response,search_path)=self.executor(lst,tc,s,variable_value_dict,request_to_sub,verdict,steps_type,parrent_tc,search_path,search_index)
                '''
                if verdict[-1][0]==constants.FAILED:
                    #verdict.append((constants.FAILED,'Failed: the test case failed because execution step failed'))
                    self.logger.debug("The test case %s failed for build %s in execution step, will do test cleanup directly." % (tc.FormattedID,self.data["ts"]["Build"]))
                    self.cleaner(lst_of_par, tc,testset_under_test,s,variable_value_dict)
                '''
                if verdict[-1][0]==constants.BLOCKED:
                    #verdict.append((constants.BLOCKED,'Blocked: the test case is blocked because the restful api call failed to run'))
                    self.logger.debug("The test case %s is blocked for build %s, will skip it." % (tc.FormattedID,self.data["ts"]["Build"]))                                        
                #elif verdict[-1][0]==constants.SUCCESS:
                else:
                    verdict,variable_value_dict=self.firstLevelCheck(lst_of_par, response, verdict, tc,s,variable_value_dict,r_ver_content,parrent_tc,steps_type,search_path,search_index)
                    if verdict[-1][0]==constants.SUCCESS:
                        verdict=self.verificator(lst_of_par, response, verdict, tc,s,variable_value_dict,search_path,parrent_tc,steps_type,search_index)
                #self.cleaner(lst_of_par, tc,testset_under_test,s)
            else:
                #verdict.append((constants.BLOCKED,'Blocked: the test case is blocked because the test setup failed'))
                self.logger.debug("The test case %s is blocked for build %s, will skip it." % (tc.FormattedID,self.data["ts"]["Build"]))
            return verdict,variable_value_dict                 

        if steps_type==constants.STEPS_EXE_FLC_VER: #run only execution, firstlevelcheck and verification
            lst=tc.c_QATCPARAMSTEXT.split('|')
            #s = requests.session()
            #setup_result,lst=self.setup(lst, tc, testset_under_test, s)
            #if setup_result==True:
            (verdict,lst_of_par,variable_value_dict,r_ver_content,response,search_path)=self.executor(lst,tc,s,variable_value_dict,request_to_sub,verdict,steps_type,parrent_tc,search_path,search_index)
            '''
            if verdict[-1][0]==constants.FAILED:
                #verdict.append((constants.FAILED,'Failed: the test case failed because execution step failed'))
                self.logger.debug("The test case %s failed for build %s in execution step, will do test cleanup directly." % (tc.FormattedID,self.data["ts"]["Build"]))
                self.cleaner(lst_of_par, tc,testset_under_test,s,variable_value_dict)
            '''
            if verdict[-1][0]==constants.BLOCKED:
                #verdict.append((constants.BLOCKED,'Blocked: the test case is blocked because the restful api call failed to run'))
                self.logger.debug("The test case %s is blocked for build %s, will skip it." % (tc.FormattedID,self.data["ts"]["Build"]))                                        
            #elif verdict[-1][0]==constants.SUCCESS:
            else:
                verdict,variable_value_dict=self.firstLevelCheck(lst_of_par, response, verdict, tc,s,variable_value_dict,r_ver_content,parrent_tc,steps_type,search_path,search_index)
                if verdict[-1][0]==constants.SUCCESS:
                    verdict=self.verificator(lst_of_par, response, verdict, tc,s,variable_value_dict,search_path,parrent_tc,steps_type,search_index)
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
                            s = requests.session()
                            variable_value_dict={}
                            variable_value_dict.setdefault(tc.Name,[]).append({})                            
                            variable_value_dict[tc.Name]=self.helper_obj.remove_number_key_of_dict(self.helper_obj.list_to_dict(variable_value_dict[tc.Name])) 
                            search_path=tc.Name
                            verdict,variable_value_dict=self.runTC(tc, verdict, testset_under_test,constants.STEPS_SUP_EXE_FLC_VER_CLU,variable_value_dict,s,"",None,search_path,None)
                            if verdict[-1][0]==constants.BLOCKED:
                                verdict[-1]=(verdict[-1][0],"Blocked: "+verdict[-1][1])
                            if verdict[-1][0]==constants.SUCCESS:
                                verdict[-1]=(verdict[-1][0],"Success: "+verdict[-1][1])       
                            if verdict[-1][0]==constants.FAILED:
                                verdict[-1]=(verdict[-1][0],"Failed: "+verdict[-1][1])                               
                            break
                                                        
                else:
                    s = requests.session()
                    variable_value_dict={}
                    variable_value_dict.setdefault(tc.Name,[]).append({})
                    variable_value_dict[tc.Name]=self.helper_obj.remove_number_key_of_dict(self.helper_obj.list_to_dict(variable_value_dict[tc.Name])) 
                    search_path=tc.Name
                    verdict,variable_value_dict=self.runTC(tc, verdict, testset_under_test,constants.STEPS_SUP_EXE_FLC_VER_CLU,variable_value_dict,s,"",None,search_path,None)
                    if verdict[-1][0]==constants.BLOCKED:
                        verdict[-1]=(verdict[-1][0],"Blocked: "+verdict[-1][1])
                    if verdict[-1][0]==constants.SUCCESS:
                        verdict[-1]=(verdict[-1][0],"Success: "+verdict[-1][1])       
                    if verdict[-1][0]==constants.FAILED:
                        verdict[-1]=(verdict[-1][0],"Failed: "+verdict[-1][1])                                     
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
                            if len(update_df['df']['Notes'])>constants.MAX_NOTE_LENGTH:
                                #need to add more logic here!!!
                                raise Exception("Length of notes in defect %s is more than the limit of %s" % (df.FormattedID,constants.MAX_NOTE_LENGTH))
                            else:
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
            

