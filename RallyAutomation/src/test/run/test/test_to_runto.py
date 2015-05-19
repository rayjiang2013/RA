'''
Created on Jan 20, 2015

@author: ljiang
'''

import pytest
from src.test.run.testSet import testSet
from copy import deepcopy
import sys
import inspect
from src.test.run.testCaseResult import testCaseResult
import datetime

from test_fixture_base import test_config_module    
from src.test.run.testObject import testObject
from src.test.run.testCase import testCase       
import src.test.run.constants as constants
import requests
 
import re
#import logging
#from src.test.run.rallyLogger import *

#Test testObject/runTO
class TestTOrunTO:
    @pytest.fixture(scope="class",params=['TS1205'])
    def config_class(self,test_config_module,request):
        try:
            print ("setup_class    class:%s" % self.__class__.__name__)
            #global ts_obj,ts,tcs,fids,new_self_data,ts_new
            (rally,data)=test_config_module
            
            data_to_runto=deepcopy(data) #use deepcopy instead of shallow one to create two separate object
            data_to_runto['ts']['FormattedID']=request.param
            
            ts_obj=testSet(rally,data_to_runto)
            ts=ts_obj.getTSByID(data_to_runto['ts']['FormattedID'])[0]
                        
            to_obj=testObject(rally,data_to_runto)
            #ts_new=to_obj.copyTS()
            #(verd,new_data)=config_module[0].runTO(ts_new)
            #global new_self_data
            
            def fin():
                try:
                    print ("teardown_class class:%s" % self.__class__.__name__)
                    #ts_new_obj=testSet(rally,data_to_runto)
                    #ts_new_obj.delTS()
            
                except Exception,details:
                    
                    print details
                    sys.exit(1)    
                    
            request.addfinalizer(fin)
            
            return (ts,to_obj,ts_obj,data_to_runto)#verd,new_data)
        except Exception,details:
            
            print details
            sys.exit(1)            


    @pytest.fixture(scope="function")
    def config_test_testobject_runto_blocked(self,test_config_module,config_class,request):
        try:
            print ("setup_method    method:%s" % inspect.stack()[0][3])
            (ts,to_obj,ts_obj,data_to_runto)=config_class
            #rally=test_config_module[1]
            tcr_data={"Build":data_to_runto['ts']['Build'],
                      "Verdict":"Blocked",
                      "TestSet":ts._ref,
                      "TestCase":ts.TestCases[0]._ref,
                      'Date':datetime.datetime.now().isoformat()
                      }
            new_self_block_data=deepcopy(data_to_runto)
            new_self_block_data['tcresult'].update(tcr_data)
            #create blocked tcr
            tcr_obj=testCaseResult(to_obj.rally,new_self_block_data)
            tcr_block=tcr_obj.createTCResult()
            
            #new ts with block tcr
            ts_obj=testSet(to_obj.rally,new_self_block_data)
            ts_with_block=ts_obj.getTSByID(new_self_block_data['ts']['FormattedID'])[0]
            
            #new to_obj
            to_obj_after_add_block_tcr=testObject(to_obj.rally,new_self_block_data)
            
            def fin():
                try:
                    inspect_elements=inspect.stack()
                    print ("teardown_method method:%s" % inspect_elements[0][3])
                    new_self_block_data['tcresult'].update({"oid":tcr_block.oid})
                    ts_new_obj=testCaseResult(to_obj.rally,new_self_block_data)
                    ts_new_obj.delTCR()
            
                except Exception,details:
                    
                    print details
                    sys.exit(1)    
                    
            request.addfinalizer(fin)
            
            return ts_with_block,to_obj_after_add_block_tcr
        except Exception,details:
            
            print details
            sys.exit(1)    



    @pytest.fixture(scope="class",params=['TS1366'])
    def config_test_testobject_runtc(self,test_config_module,request):
        try:
            print ("setup_method    method: %s" % inspect.stack()[0][3])
            #global ts_obj,ts,tcs,fids,new_self_data,ts_new
            (rally,data)=test_config_module
            
            data_to_runtc=deepcopy(data) #use deepcopy instead of shallow one to create two separate object
            data_to_runtc['ts']['FormattedID']=request.param
            ts_obj=testSet(rally,data_to_runtc)
            ts=ts_obj.getTSByID(request.param)[0]

            def fin():
                try:
                    
                    print ("teardown_method method: %s" % inspect.stack()[0][3])    
                    #print ("teardown_method method: %s" % inspect.stack()[0][3])
                    ts=ts_obj.getTSByID(request.param)[0]
                    tcs=ts_obj.allTCofTS(ts)
                    for tc in tcs:
                        if tc.Name=='Test Case Dummy':
                            data_to_runtc['tc']['FormattedID']=tc.FormattedID
                            tc_obj=testCase(rally,data_to_runtc)
                            tc_obj.delTC()
                    
                except Exception,details:                    
                    print details
                    sys.exit(1)  
                    
            request.addfinalizer(fin)        
            
            return ts,data_to_runtc,ts_obj
        except Exception,details:
            
            print details
            sys.exit(1)    

    @pytest.mark.parametrize("c_QATCPARAMSTEXT", ['DELETE|/logout|||200|{"okay":true}||||||||||||login||{"wrong_user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||',#this case is expected to fail
                                                  'NONEXIST|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||',
                                                  'DELETE|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$nonexist","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||',
                                                  'DELETE|/logout|||200|{"okay":true}||||||||||||login|||||||||||||||||||||||||||||||||',
                                                  'DELETE|/logout|||200|{"okay":true}||||||||||||||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||',
                                                  'DELETE|/nonexist|||200|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||',
                                                  'DELETE|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$nonexist_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||',
                                                  'DELETE|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","wrong_key":"$admin_password"}|||||||||||||||||||||||||||||||',
                                                  'DELETE|/logout|||200|{"okay":true}||||||||||||UNEXPECTED||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||',
                                                  'DELETE|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$nonexist_password"}|||||||||||||||||||||||||||||||',
                                                  'DELETE|/logout|||200|{"okay":false}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||',
                                                  'DELETE|/logout|||UNEXPECTED|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||',
                                                  'DELETE|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||'])
                                                      
    def test_testobject_runtc_logout(self,config_test_testobject_runtc,c_QATCPARAMSTEXT,test_config_module):
        print 'test_testobject_runtc_logout  <============================ actual test code'      
        rally=test_config_module[0]
        ts,data_to_runtc,ts_obj=config_test_testobject_runtc  
        data_to_runtc['tc']={
            "Description": "Test Case Dummy",
            "Expedite": "false",
            "FormattedID": "",
            "LastBuild": "",
            "Method": "Automated",
            "Name": "Test Case Dummy",
            "Objective": "",
            "TestFolder": "",
            "Type": "Acceptance",
            "c_QATCPARAMSTEXT":c_QATCPARAMSTEXT}
                   
        to_obj=testObject(rally,data_to_runtc)           
        #runTC(self,tc,verdict,testset_under_test,steps_type,variable_value_dict,s)
        tc_obj=testCase(rally,data_to_runtc)
        tc=tc_obj.createTC()
        new_ts=ts_obj.addSpecificTCs([tc],ts)
        
        s = requests.session()
        
        variable_value_dict={}
        variable_value_dict.setdefault(tc.Name,[]).append({})
        variable_value_dict[tc.Name]=to_obj.remove_number_key_of_dict(to_obj.list_to_dict(variable_value_dict[tc.Name])) 
        search_path=tc.Name
        verdict,variable_value_dict=to_obj.runTC(tc, [], new_ts, constants.STEPS_SUP_EXE_FLC_VER_CLU, variable_value_dict, s,[],None,search_path)        
        
        #verdict,variable_value_dict=to_obj.runTC(tc, [], new_ts, constants.STEPS_SUP_EXE_FLC_VER_CLU, {}, s,[])
        pass
        if c_QATCPARAMSTEXT=='DELETE|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$nonexist","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||':
            assert verdict == [(constants.BLOCKED,'fail to setup as nonexist is/are not defined in extra.json or pre-defined local variables')]
        if c_QATCPARAMSTEXT=='DELETE|/logout|||200|{"okay":true}||||||||||||||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||':
            assert verdict == [(constants.SUCCESS,'as not enough setup information is provided, the test setup is skipped; execution is successful; status code expected and first level check succeed; no verification is done.')]
        if c_QATCPARAMSTEXT=='DELETE|/logout|||200|{"okay":true}||||||||||||login|||||||||||||||||||||||||||||||||':
            assert verdict==[(constants.SUCCESS,u'the test case is setup successfully; execution is successful; status code expected and first level check succeed; no verification is done.')]
        if c_QATCPARAMSTEXT=='DELETE|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","wrong_key":"$admin_password"}|||||||||||||||||||||||||||||||':
            assert verdict == [(constants.BLOCKED, 'fail to setup as the restful api level test case TC2118 (login) failed: fail to execute as unable to save values in response content to variables as the variable: role cannot be found in the response content, id cannot be found in the response content, email cannot be found in the response content; status code unexpected. The unexpected status code of the response is 401')]
        if c_QATCPARAMSTEXT=='DELETE|/logout|||200|{"okay":true}||||||||||||login||{"wrong_user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||':
            assert verdict==[(constants.BLOCKED, 'fail to setup as the restful api level test case TC2118 (login) failed: fail to execute as unable to save values in response content to variables as the variable: role cannot be found in the response content, id cannot be found in the response content, email cannot be found in the response content; status code unexpected. The unexpected status code of the response is 401')]  #expected to fail
        if c_QATCPARAMSTEXT=='DELETE|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$nonexist_password"}|||||||||||||||||||||||||||||||':
            assert verdict==[(constants.BLOCKED, 'fail to setup as the restful api level test case TC2118 (login) failed: fail to execute as unable to save values in response content to variables as the variable: role cannot be found in the response content, id cannot be found in the response content, email cannot be found in the response content; status code unexpected. The unexpected status code of the response is 401')]
        if c_QATCPARAMSTEXT=='DELETE|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$nonexist_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||':
            assert verdict==[(constants.BLOCKED, u'fail to setup as the restful api level test case TC2118 (login) failed: fail to execute as unable to save values in response content to variables as the variable: role cannot be found in the response content, id cannot be found in the response content, email cannot be found in the response content; status code unexpected. The unexpected status code of the response is 401')]
        if c_QATCPARAMSTEXT=='DELETE|/logout|||200|{"okay":true}||||||||||||UNEXPECTED||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||':
            assert verdict==[(constants.BLOCKED, 'fail to setup as the api call is unexpected')]
        if c_QATCPARAMSTEXT=='DELETE|/logout|||200|{"okay":false}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||':
            assert verdict==[(constants.FAILED, u"the test case is setup successfully; execution is successful; status code expected but first level check failed. Error: 'okay' : True in content of response is different from the expected.")]
        if c_QATCPARAMSTEXT=='NONEXIST|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||':
            assert verdict==[(constants.BLOCKED,'fail to execute as unexpected execution method: NONEXIST')]
        if c_QATCPARAMSTEXT=='DELETE|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||':
            assert verdict==[(constants.SUCCESS,'the test case is setup successfully; execution is successful; status code expected and first level check succeed; no verification is done.')]
        if c_QATCPARAMSTEXT=='DELETE|/nonexist|||200|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||':
            assert verdict==[(constants.FAILED, u'the test case is setup successfully; execution is successful; status code unexpected. The unexpected status code of the response is 404')]              
        if c_QATCPARAMSTEXT=='DELETE|/logout|||UNEXPECTED|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||':
            assert verdict==[(constants.BLOCKED, 'the test case is setup successfully; execution is successful; status code is expected to be digits instead of something else: UNEXPECTED')]           


    @pytest.mark.parametrize("c_QATCPARAMSTEXT", ['POST|/nonexist|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}||||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}||200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$nonexist_email"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"UNEXPECTED":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":false,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|UNEXPECTED|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'NONEXIST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||UNEXPECTED|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"wrong_key":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',  #This is expected fail
                                                  'POST||{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  '|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]||{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',                                                  
                                                  'POST|/login|{"user[email]":"$nonexist_email","user[password]":"nonexist_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login||user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"$admin_email"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||'])    
    def test_testobject_runtc_login(self,config_test_testobject_runtc,c_QATCPARAMSTEXT,test_config_module):
        print 'test_testobject_runtc_login  <============================ actual test code'      
        rally=test_config_module[0]
        ts,data_to_runtc,ts_obj=config_test_testobject_runtc  
        data_to_runtc['tc']={
            "Description": "Test Case Dummy",
            "Expedite": "false",
            "FormattedID": "",
            "LastBuild": "",
            "Method": "Automated",
            "Name": "Test Case Dummy",
            "Objective": "",
            "TestFolder": "",
            "Type": "Acceptance",
            "c_QATCPARAMSTEXT":c_QATCPARAMSTEXT}
                   
        to_obj=testObject(rally,data_to_runtc)           
        #runTC(self,tc,verdict,testset_under_test,steps_type,variable_value_dict,s)
        tc_obj=testCase(rally,data_to_runtc)
        tc=tc_obj.createTC()
        new_ts=ts_obj.addSpecificTCs([tc],ts)
        
        s = requests.session()
        
        variable_value_dict={}
        variable_value_dict.setdefault(tc.Name,[]).append({})
        variable_value_dict[tc.Name]=to_obj.remove_number_key_of_dict(to_obj.list_to_dict(variable_value_dict[tc.Name])) 
        search_path=tc.Name
        verdict,variable_value_dict=to_obj.runTC(tc, [], new_ts, constants.STEPS_SUP_EXE_FLC_VER_CLU, variable_value_dict, s,[],None,search_path)            

        #verdict,variable_value_dict=to_obj.runTC(tc, [], new_ts, constants.STEPS_SUP_EXE_FLC_VER_CLU, {}, s,[])
        #pass
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]||{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.BLOCKED,u'as not enough setup information is provided, the test setup is skipped; execution is successful; status code is expected to be digits instead of something else: ')]
        if c_QATCPARAMSTEXT=='POST|/login||user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.BLOCKED,'fail to execute as JSON object to make POST request is missing')]
        if c_QATCPARAMSTEXT=='POST||{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.BLOCKED,'fail to execute as no path is provided')]
        if c_QATCPARAMSTEXT=='|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.BLOCKED,'fail to execute as no execution method is provided')]
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$nonexist_email","user[password]":"nonexist_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,'fail to execute as unable to save values in response content to variables as the variable: role cannot be found in the response content, id cannot be found in the response content, email cannot be found in the response content; status code unexpected. The unexpected status code of the response is 401')]
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$admin_email"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,'fail to execute as unable to save values in response content to variables as the variable: role cannot be found in the response content, id cannot be found in the response content, email cannot be found in the response content; status code unexpected. The unexpected status code of the response is 401')]
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,'fail to execute as unable to save values in response content to variables as the variable: role cannot be found in the response content, id cannot be found in the response content, email cannot be found in the response content; status code unexpected. The unexpected status code of the response is 401')] 
        if c_QATCPARAMSTEXT=='POST|/login|{"wrong_key":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,'fail to execute as unable to save values in response content to variables as the variable: role cannot be found in the response content, id cannot be found in the response content, email cannot be found in the response content; status code unexpected. The unexpected status code of the response is 401')]  #expected to fail
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||UNEXPECTED|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,'as not enough setup information is provided, the test setup is skipped; execution is successful; status code expected and first level check succeed; verification failed, error: the api level test case name UNEXPECTED cannot be found in API test set TS1103')]
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}||||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict[0][0] == constants.FAILED and re.match(r"as not enough setup information is provided, the test setup is skipped; execution is successful; status code expected and first level check succeed; verification failed, error: the api level test case GetCurrentUser failed: execution is successful; id, email, role is/are not defined in extra.json or pre-defined local variables; status code expected but first level check failed. Error: 'id' : \w+ in content of response is different from the expected. 'role' : admin in content of response is different from the expected. 'email' : admin@spirent.com in content of response is different from the expected.", verdict[0][1])
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,"as not enough setup information is provided, the test setup is skipped; execution is successful; status code expected and first level check succeed; verification failed, error: the api level test case GetCurrentUser failed: execution is successful; role is/are not defined in extra.json or pre-defined local variables; status code expected but first level check failed. Error: 'role' : admin in content of response is different from the expected.")]
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}||200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,"as not enough setup information is provided, the test setup is skipped; execution is successful; user[email] is/are not defined in extra.json or pre-defined local variables; status code expected but first level check failed. Error: 'email' : admin@spirent.com in content of response is different from the expected.")]
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$nonexist_email"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,u"as not enough setup information is provided, the test setup is skipped; execution is successful; status code expected but first level check failed. Error: 'email' : admin@spirent.com in content of response is different from the expected.")]
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"UNEXPECTED":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,u"as not enough setup information is provided, the test setup is skipped; execution is successful; status code expected but first level check failed. Error: 'UNEXPECTED' : {u'email': u'admin@spirent.com'} is missing from content of response.")]
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":false,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,"as not enough setup information is provided, the test setup is skipped; execution is successful; status code expected but first level check failed. Error: 'okay' : True in content of response is different from the expected.")]
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|UNEXPECTED|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.BLOCKED,'as not enough setup information is provided, the test setup is skipped; execution is successful; status code is expected to be digits instead of something else: UNEXPECTED')]         
        if c_QATCPARAMSTEXT=='POST|/nonexist|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,'as not enough setup information is provided, the test setup is skipped; execution is successful; status code unexpected. The unexpected status code of the response is 404')]        
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.SUCCESS,'as not enough setup information is provided, the test setup is skipped; execution is successful; status code expected and first level check succeed; verification is successful.')]
        if c_QATCPARAMSTEXT=='NONEXIST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.BLOCKED,'fail to execute as unexpected execution method: NONEXIST')]     


    @pytest.mark.parametrize("c_QATCPARAMSTEXT", ['POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||UNEXPECTED|||||||||||||||||||||||||||||||||||||'])
    def test_testobject_runtc_login_negative(self,config_test_testobject_runtc,c_QATCPARAMSTEXT,test_config_module):
        print 'test_testobject_runtc_login_negative  <============================ actual test code'      
        rally=test_config_module[0]
        ts,data_to_runtc,ts_obj=config_test_testobject_runtc  
        data_to_runtc['tc']={
            "Description": "Test Case Dummy",
            "Expedite": "false",
            "FormattedID": "",
            "LastBuild": "",
            "Method": "Automated",
            "Name": "Test Case Dummy",
            "Objective": "",
            "TestFolder": "",
            "Type": "Acceptance",
            "c_QATCPARAMSTEXT":c_QATCPARAMSTEXT}
                   
        to_obj=testObject(rally,data_to_runtc)           
        #runTC(self,tc,verdict,testset_under_test,steps_type,variable_value_dict,s)
        tc_obj=testCase(rally,data_to_runtc)
        tc=tc_obj.createTC()
        new_ts=ts_obj.addSpecificTCs([tc],ts)
        
        s = requests.session()
        variable_value_dict={}
        variable_value_dict.setdefault(tc.Name,[]).append({})
        variable_value_dict[tc.Name]=to_obj.remove_number_key_of_dict(to_obj.list_to_dict(variable_value_dict[tc.Name])) 
        search_path=tc.Name
        #verdict,variable_value_dict=to_obj.runTC(tc, [], new_ts, constants.STEPS_SUP_EXE_FLC_VER_CLU, variable_value_dict, s,[],None,search_path)    

        with pytest.raises(Exception) as excinfo:
            #to_obj.runTC(tc, [], new_ts, constants.STEPS_SUP_EXE_FLC_VER_CLU, {}, s,[])
            to_obj.runTC(tc, [], new_ts, constants.STEPS_SUP_EXE_FLC_VER_CLU, variable_value_dict, s,[],None,search_path)
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||UNEXPECTED|||||||||||||||||||||||||||||||||||||':
            assert "failed to clean up because the api level test case name UNEXPECTED cannot be found in API test set" in excinfo.value.message     
        

    @pytest.mark.parametrize("c_QATCPARAMSTEXT", ['POST|/users|{"user[email]":"$standard_email","user[firstname]":"$standard_firstname","user[lastname]":"$standard_lastname","user[role]":"$standard_role","user[password]":"$standard_password"}|user[email];UNEXPECTED;user[lastname]|200|{"firstname":"$user[firstname]","lastname":"$user[lastname]","email":"$user[email]"}|id;role;firstname;lastname;email|||GetUser|||DeleteUser;logout|||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}||||||||||||||||||||||||||||||',
                                                  'POST|/users|{"user[email]":"$standard_email","user[firstname]":"$standard_firstname","user[lastname]":"$standard_lastname","user[role]":"$standard_role","user[password]":"$standard_password"}||200|{"firstname":"$user[firstname]","lastname":"$user[lastname]","email":"$user[email]"}|id;role;firstname;lastname;email|||GetUser|||DeleteUser;logout|||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}||||||||||||||||||||||||||||||',
                                                  'POST|/users|{"user[email]":"$standard_email","user[firstname]":"$standard_firstname","user[lastname]":"$standard_lastname","user[role]":"$standard_role","user[password]":"$standard_password"}|user[email];user[lastname]|200|{"firstname":"$user[firstname]","lastname":"$user[lastname]","email":"$user[email]"}|id;role;firstname;lastname;email|||GetUser|||DeleteUser;logout|||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}||||||||||||||||||||||||||||||',
                                                  'POST|/users|{"user[email]":"$standard_email","user[firstname]":"$standard_firstname","user[lastname]":"$standard_lastname","user[role]":"$standard_role","user[password]":"$standard_password"}|user[email];user[firstname];user[lastname]|200|{"firstname":"$user[firstname]","lastname":"$user[lastname]","email":"$user[email]"}|id;role;firstname;lastname;email|||GetUser|||DeleteUser;logout|||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}||||||||||||||||||||||||||||||'])  
    def test_testobject_runtc_CreateUser(self,config_test_testobject_runtc,c_QATCPARAMSTEXT,test_config_module):
        print 'test_testobject_runtc_CreateUser  <============================ actual test code'      
        rally=test_config_module[0]
        ts,data_to_runtc,ts_obj=config_test_testobject_runtc  
        data_to_runtc['tc']={
            "Description": "Test Case Dummy",
            "Expedite": "false",
            "FormattedID": "",
            "LastBuild": "",
            "Method": "Automated",
            "Name": "Test Case Dummy",
            "Objective": "",
            "TestFolder": "",
            "Type": "Acceptance",
            "c_QATCPARAMSTEXT":c_QATCPARAMSTEXT}
                   
        to_obj=testObject(rally,data_to_runtc)           
        #runTC(self,tc,verdict,testset_under_test,steps_type,variable_value_dict,s)
        tc_obj=testCase(rally,data_to_runtc)
        tc=tc_obj.createTC()
        new_ts=ts_obj.addSpecificTCs([tc],ts)
        
        s = requests.session()

        variable_value_dict={}
        variable_value_dict.setdefault(tc.Name,[]).append({})
        variable_value_dict[tc.Name]=to_obj.remove_number_key_of_dict(to_obj.list_to_dict(variable_value_dict[tc.Name])) 
        search_path=tc.Name
        verdict,variable_value_dict=to_obj.runTC(tc, [], new_ts, constants.STEPS_SUP_EXE_FLC_VER_CLU, variable_value_dict, s,[],None,search_path)            
    
        #verdict,variable_value_dict=to_obj.runTC(tc, [], new_ts, constants.STEPS_SUP_EXE_FLC_VER_CLU, {}, s,[])
        #pass
        if c_QATCPARAMSTEXT=='POST|/users|{"user[email]":"$standard_email","user[firstname]":"$standard_firstname","user[lastname]":"$standard_lastname","user[role]":"$standard_role","user[password]":"$standard_password"}|user[email];UNEXPECTED;user[lastname]|200|{"firstname":"$user[firstname]","lastname":"$user[lastname]","email":"$user[email]"}|id;role;firstname;lastname;email|||GetUser|||DeleteUser;logout|||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,"the test case is setup successfully; execution is successful, UNEXPECTED cannot be found in the requested json object; user[firstname] is/are not defined in extra.json or pre-defined local variables; status code expected but first level check failed. Error: 'firstname' : standard in content of response is different from the expected.")]
        if c_QATCPARAMSTEXT=='POST|/users|{"user[email]":"$standard_email","user[firstname]":"$standard_firstname","user[lastname]":"$standard_lastname","user[role]":"$standard_role","user[password]":"$standard_password"}||200|{"firstname":"$user[firstname]","lastname":"$user[lastname]","email":"$user[email]"}|id;role;firstname;lastname;email|||GetUser|||DeleteUser;logout|||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,u"the test case is setup successfully; execution is successful; user[firstname], user[lastname] is/are not defined in extra.json or pre-defined local variables; status code expected but first level check failed. Error: 'firstname' : standard in content of response is different from the expected. 'lastname' : standard in content of response is different from the expected. 'email' : standard@spirent.com in content of response is different from the expected.")]
        if c_QATCPARAMSTEXT=='POST|/users|{"user[email]":"$standard_email","user[firstname]":"$standard_firstname","user[lastname]":"$standard_lastname","user[role]":"$standard_role","user[password]":"$standard_password"}|user[email];user[lastname]|200|{"firstname":"$user[firstname]","lastname":"$user[lastname]","email":"$user[email]"}|id;role;firstname;lastname;email|||GetUser|||DeleteUser;logout|||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,"the test case is setup successfully; execution is successful; user[firstname] is/are not defined in extra.json or pre-defined local variables; status code expected but first level check failed. Error: 'firstname' : standard in content of response is different from the expected.")]
        if c_QATCPARAMSTEXT=='POST|/users|{"user[email]":"$standard_email","user[firstname]":"$standard_firstname","user[lastname]":"$standard_lastname","user[role]":"$standard_role","user[password]":"$standard_password"}|user[email];user[firstname];user[lastname]|200|{"firstname":"$user[firstname]","lastname":"$user[lastname]","email":"$user[email]"}|id;role;firstname;lastname;email|||GetUser|||DeleteUser;logout|||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}||||||||||||||||||||||||||||||':
            assert verdict == [(constants.SUCCESS,'the test case is setup successfully; execution is successful; status code expected and first level check succeed; verification is successful.')]


    @pytest.mark.parametrize("c_QATCPARAMSTEXT,expected", [('DELETE|/users/$id[1]|||200|{"okay":true}|||||||logout|||||login;CreateUser||{"user[email]":"$admin_email","user[password]":"$admin_password"};{"user[email]":"$standard_email","user[firstname]":"$standard_firstname","user[lastname]":"$standard_lastname","user[role]":"$standard_role","user[password]":"$standard_password"}||||||||||||||||||||||||||||||',[(constants.SUCCESS,'the test case is setup successfully; execution is successful; status code expected and first level check succeed; no verification is done.')])])
    def test_testobject_runtc_DeleteUser(self,config_test_testobject_runtc,c_QATCPARAMSTEXT,test_config_module,expected):
        print 'test_testobject_runtc_DeleteUser  <============================ actual test code'      
        rally=test_config_module[0]
        ts,data_to_runtc,ts_obj=config_test_testobject_runtc  
        data_to_runtc['tc']={
            "Description": "Test Case Dummy",
            "Expedite": "false",
            "FormattedID": "",
            "LastBuild": "",
            "Method": "Automated",
            "Name": "Test Case Dummy",
            "Objective": "",
            "TestFolder": "",
            "Type": "Acceptance",
            "c_QATCPARAMSTEXT":c_QATCPARAMSTEXT}
                   
        to_obj=testObject(rally,data_to_runtc)           
        #runTC(self,tc,verdict,testset_under_test,steps_type,variable_value_dict,s)
        tc_obj=testCase(rally,data_to_runtc)
        tc=tc_obj.createTC()
        new_ts=ts_obj.addSpecificTCs([tc],ts)
        
        s = requests.session()
        variable_value_dict={}
        variable_value_dict.setdefault(tc.Name,[]).append({})
        variable_value_dict[tc.Name]=to_obj.remove_number_key_of_dict(to_obj.list_to_dict(variable_value_dict[tc.Name])) 
        search_path=tc.Name
        verdict,variable_value_dict=to_obj.runTC(tc, [], new_ts, constants.STEPS_SUP_EXE_FLC_VER_CLU, variable_value_dict, s,[],None,search_path)
        #pass
        #if c_QATCPARAMSTEXT=='DELETE|/users/$id|||200|{"okay":true}|||||||logout|||||login;CreateUser||{"user[email]":"$admin_email","user[password]":"$admin_password"};{"user[email]":"$standard_email","user[firstname]":"$standard_firstname","user[lastname]":"$standard_lastname","user[role]":"$standard_role","user[password]":"$standard_password"}||||||||||||||||||||||||||||||':
        assert verdict == expected




    @pytest.mark.parametrize("search_path_list,variable_value_dict,local_variable_dict,current_api_call,return_value", [(["Test Case Dummy","login","GetCurrentUser"],{"Test Case Dummy":{"login":{"GetCurrentUser":{"whatever":"whatever"}}}},{"whatever":"whatever"},"login",{'Test Case Dummy': {'login': {'GetCurrentUser': {'login': {'whatever': 'whatever'}, 'whatever': 'whatever'}}}})])
    def test_testobject_append_local_variable_dict_to_variable_value_dict(self,config_class,search_path_list,variable_value_dict,local_variable_dict,current_api_call,return_value):
        print 'test_testobject_list_to_dict  <============================ actual test code'                         
        (ts,to_obj,ts_obj,data_to_runto)=config_class
        verdict=to_obj.append_local_variable_dict_to_variable_value_dict(search_path_list,variable_value_dict,local_variable_dict,current_api_call)
        assert verdict == return_value



    @pytest.mark.parametrize("d1,d2,error_message", [({"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"},{"l":"r"},{"p":"q"},{"n":"o"}]},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":[{"n":"o"},{"l":"m"}]}}," 'i' : j is missing from content of response. 'l' : r is missing from content of response. 'p' : q is missing from content of response."),
                                                     ({"a":"b","c":"d","e":[{"k":[{"l":"m"},{"l":"r"},{"p":"q"},{"n":"o"}],"f":"g","i":"j"},{"s":"t"}]},{"i":"j","a":"b","c":"d","e":{"f":"g","i":"j","k":[{"n":"o"},{"l":["m","r"]},{"p":"q"}]}}," 's' : t is missing from content of response."),
                                                     ({"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"},{"p":"q"},{"n":"o"}]},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":[{"n":"o"},{"l":"m"}]}}," 'i' : j is missing from content of response. 'p' : q is missing from content of response."),
                                                     ({"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"},{"n":"o"}]},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"}]}}," 'i' : j is missing from content of response. 'n' : o is missing from content of response."),
                                                     ({"a":"b","c":"d","e":{"f":"g","k":{"l":"m"}},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"}]}}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"}]},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"}]}}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","e":['f','g'],"i":"j"},{"a":"b","c":"d","e":['g']}," 'i' : j is missing from content of response. 'f' is missing from content of response."),
                                                     ({"a":"b","c":"d","e":[{"k":[{"l":"m"},{"l":"r"},{"p":"q"},{"n":"o"}],"f":"g","i":"j"},{"s":"t"}]},{"i":"j","c":"d","a":"b","e":[{"f":"g","i":"j","k":[{"n":"o"},{"l":["m","r"]},{"p":"q"}]},{"s":"t"}]},""),                                                     
                                                     ({"a":"b","c":"d","e":{"k":[{"l":"m"},{"l":"r"},{"p":"q"},{"n":"o"}],"f":"g","i":"j"}},{"i":"j","a":"b","c":"d","e":{"f":"g","i":"j","k":[{"n":"o"},{"l":["m","r"]},{"p":"q"}]}},""),
                                                     ({"a":"b","c":"d","e":{"k":[{"l":"m"},{"l":"r"},{"p":"q"},{"n":"o"}],"f":"g","i":"j"}},{"i":"j","a":"b","c":"d","e":{"f":"g","i":"j","k":[{"n":"o"},{"l":"m"},{"l":"r"},{"p":"q"}]}},""),
                                                     ({"a":"b","c":"d","e":{"k":[{"l":"m"},{"l":"r"},{"p":"q"},{"n":"o"}],"f":"g","i":"j"}},{"i":"j","a":"b","c":"d","e":{"f":"g","k":[{"n":"o"},{"l":"m"},{"l":"r"},{"p":"q"}]}}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","i":"j","e":{"k":[{"l":"m"},{"l":"r"},{"p":"q"},{"n":"o"}],"f":"g"}},{"a":"b","c":"d","e":{"f":"g","k":[{"n":"o"},{"l":"m"},{"l":"r"},{"p":"q"}]}}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"},{"l":"r"},{"p":"q"},{"n":"o"}]},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":[{"n":"o"},{"l":"m"},{"l":"r"},{"p":"q"}]}}," 'i' : j is missing from content of response."),                                                     
                                                     ({"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"},"p",{"n":"o"}]},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":[{"n":"o"},{"l":"m"}]}}," 'i' : j is missing from content of response. 'p' is missing from content of response."),
                                                     ({"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"},{"n":"o"}]},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":[{"n":"o"},{"l":"m"}]}}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"},]},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"}]}}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","e":{"f":"g","k":{"l":"m"}},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":"l"}}," 'i' : j is missing from content of response. 'k' : l in content of response is different from the expected."),
                                                     ({"a":"b","c":"d","e":{"f":"g","k":"l"},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":"l"}}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","e":{"f":"g"},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":"l"}}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","e":{"f":"g","k":"l"},"i":"j"},{"a":"b","c":"d","e":{"f":"g"}}," 'i' : j is missing from content of response. 'k' : l is missing from content of response."),
                                                     ({"a":"b","c":"d","e":{"f":"g"},"i":"j"},{"a":"b","c":"d","e":{"f":"g"}}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","e":"f","i":"j"},{"a":"b","c":"d","e":{"f":"g"}}," 'i' : j is missing from content of response. 'e' : {'f': 'g'} in content of response is different from the expected."),
                                                     ({"a":"b","c":"d","e":['f'],"i":"j"},{"a":"b","c":"d","e":['g']}," 'i' : j is missing from content of response. 'f' is missing from content of response. 'g' in content of response is different from the expected."),
                                                     ({"a":"b","c":"d","e":['f'],"i":"j"},{"a":"b","c":"d","e":['g']}," 'i' : j is missing from content of response. 'f' is missing from content of response. 'g' in content of response is different from the expected."),
                                                     ({"a":"b","c":"d","e":['f','g'],"i":"j"},{"a":"b","c":"d","e":['f','g','h']}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","e":[],"i":"j"},{"a":"b","c":"d","e":[]}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","e":"f","i":"j"},{"a":"b","c":"d","e":[]}," 'i' : j is missing from content of response. 'e' : [] in content of response is different from the expected."),
                                                     ({"a":"b","c":"d","e":"f","i":"j"},{"a":"b","c":"d","e":["f","k"]}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","e":"f","i":"j"},{"a":"b","c":"d","g":"h"}," 'i' : j is missing from content of response. 'e' : f is missing from content of response."),
                                                     ({"a":"b","c":"d","e":"f"},{"a":"b","c":"d","g":"h"}," 'e' : f is missing from content of response."),
                                                     ({"a":"b","c":"d"},{"a":"b","c":"d","e":"f"},""),({"a":"b","c":"d"},{"a":"b","c":"d"},""),
                                                     ({"a":"b","c":"d"},{"a":"b"}," 'c' : d is missing from content of response."),
                                                     ({},{},""),
                                                     ({"a":"b"},{"a":"b"},"")])
    def test_testobject_searchDict3(self,config_class,d1,d2,error_message):
        print 'test_testobject_runtc_searchDict3  <============================ actual test code'                         
        (ts,to_obj,ts_obj,data_to_runto)=config_class
        verdict=to_obj.searchDict3(d1, d2, "")
        assert verdict == error_message

    @pytest.mark.parametrize("lst,return_value", [([{'i': 'j', 'k': [{'n': 'o'}, {'l': ['m', 'r']}, {'p': 'q'}], 'f': 'g'}, {'s': 't'}],{'1': {'i': 'j', 'k': {'1': {'n': 'o'}, '0': {'l': {'1': 'r', '0': 'm'}}, '2': {'p': 'q'}}, 'f': 'g'}, '0': {'s': 't'}})])
    def test_testobject_list_to_dict(self,config_class,lst,return_value):
        print 'test_testobject_list_to_dict  <============================ actual test code'                         
        (ts,to_obj,ts_obj,data_to_runto)=config_class
        verdict=to_obj.list_to_dict(lst)
        assert verdict == return_value


    @pytest.mark.parametrize("dt,return_value", [({'0':{}},{}),
                                                 ({'1': {'i': 'j', 'k': {'1': {'n': 'o'}, '0': {'l': {'1': 'r', '0': 'm'}}, '2': {'p': 'q'}}, 'f': 'g'}, '0': {'s': 't'}},{'f': 'g', 'i': 'j', 'k': {'p': 'q', 'l': {'1': 'r', '0': 'm'}, 'n': 'o'}, 's': 't'}),
                                                 ({'1': {'l': 'r'}, '0': {'l': 'm'}, '3': {'p': {'0':{'q':'u'},'1':{'v':'w'},'2':{'q':'u'}}}, '2': {'n': 'o'},'5': 't', '4': {'l': 's'}},{'l': ['r', 'm', 's'], 'n': 'o', 'p': {'q': ['u','u'], 'v': 'w'}, '5': 't'}),
                                                 ({'1': {'l': 'r'}, '0': {'l': 'm'}, '3': {'p': 'q'}, '2': {'n': 'o'},'5': 't', '4': {'l': 'm'}},{'l': ['r', 'm','m'], 'p': 'q', 'n': 'o','5': 't'}),
                                                 ({'1': {'l': 'r'}, '0': {'l': 'm'}, '3': {'p': {'0':{'q':'u'},'1':{'v':'w'}}}, '2': {'n': 'o'},'5': 't', '4': {'l': 's'}},{'l': ['r', 'm', 's'], 'n': 'o', 'p': {'q': 'u', 'v': 'w'}, '5': 't'}),
                                                 ({'1': {'l': 'r'}, '0': {'l': 'm'}, '3': {'p': {'0':{'q':'u'}}}, '2': {'n': 'o'},'5': 't', '4': {'l': 's'}},{'l': ['r', 'm','s'], 'p': {'q':'u'}, 'n': 'o','5': 't'}),
                                                 ({'1': {'l': 'r'}, '0': {'l': 'm'}, '3': {'p': {'q':'u'}}, '2': {'n': 'o'},'5': 't', '4': {'l': 's'}},{'l': ['r', 'm','s'], 'p': {'q':'u'}, 'n': 'o','5': 't'}),
                                                 ({'1': {'l': 'r'}, '0': {'l': 'm'}, '3': {'p': 'q'}, '2': {'n': 'o'},'5': 't', '4': {'l': 's'}},{'l': ['r', 'm','s'], 'p': 'q', 'n': 'o','5': 't'}),
                                                 ({'1': {'l': 'r'}, '0': {'l': 'm'}, '3': {'p': 'q'}, '2': {'n': 'o'}, '4': {'l': 's'}},{'l': ['r', 'm','s'], 'p': 'q', 'n': 'o'}),
                                                 ({'1': {'l': 'r'}, '0': {'l': 'm'}, '3': {'p': 'q'}, '2': {'n': 'o'}},{'l': ['r', 'm'], 'p': 'q', 'n': 'o'})])
    def test_testobject_remove_number_key_of_dict(self,config_class,dt,return_value):
        print 'test_testobject_remove_number_key_of_dict  <============================ actual test code'                         
        (ts,to_obj,ts_obj,data_to_runto)=config_class
        verdict=to_obj.remove_number_key_of_dict(dt)
        assert verdict == return_value
   
    def test_testobject_runto_equal_formattedid(self,config_class):
        print 'test_testobject_runto_equal_formattedid  <============================ actual test code'
        (ts,to_obj)=config_class[0:2]
        new_data=(to_obj.runTO(ts))[1]
        assert ts.FormattedID==new_data['ts']['FormattedID']
        
    def test_testobject_runto_same_verdict_size(self,config_class,test_config_module):
        print 'test_testobject_runto_same_verdict_size  <============================ actual test code'
        (ts,to_obj)=config_class[0:2]
        verd=(to_obj.runTO(ts))[0]
        assert len(ts.TestCases)==len(verd)

    
    def test_testobject_runto_state_in_process(self,config_class):
        print 'test_testobject_runto_state_in_process  <============================ actual test code'
        (ts,to_obj,ts_obj,data_to_runto)=config_class[0:4]
        to_obj.runTO(ts)[1]
        ts_after_runTO=ts_obj.getTSByID(data_to_runto['ts']['FormattedID'])[0]
        assert ts_after_runTO.ScheduleState=="In-Progress"
        
        
    def test_testobject_runto_blocked(self,config_test_testobject_runto_blocked):
        print 'test_testobject_runto_blocked  <============================ actual test code'
        ts_to_runto,to_obj_after_add_block_tcr=config_test_testobject_runto_blocked
        (verd,new_data)=to_obj_after_add_block_tcr.runTO(ts_to_runto)
        tcs=ts_to_runto.TestCases
        for v in verd:
            if v[0] == 2:
                sorted_trs=sorted(tcs[verd.index(v)].Results,key=lambda x: x.Date, reverse=True)
                same_build_tr_list=[]
                for tr in sorted_trs:
                    if new_data['ts']['Build']==tr.Build:
                        same_build_tr_list.append(tr)
                break
        assert same_build_tr_list[0].Verdict=="Blocked"