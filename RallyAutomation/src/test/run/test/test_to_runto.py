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

    @pytest.mark.parametrize("c_QATCPARAMSTEXT", ['NONEXIST|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||',
                                                  'DELETE|/nonexist|||200|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||',
                                                  'DELETE|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","wrong_key":"$admin_password"}|||||||||||||||||||||||||||||||',
                                                  'DELETE|/logout|||200|{"okay":true}||||||||||||||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||',
                                                  'DELETE|/logout|||200|{"okay":true}||||||||||||login|||||||||||||||||||||||||||||||||',                                                  
                                                  'DELETE|/logout|||200|{"okay":true}||||||||||||login||{"wrong_user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||',
                                                  'DELETE|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$nonexist_password"}|||||||||||||||||||||||||||||||',
                                                  'DELETE|/logout|||200|{"okay":false}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||',
                                                  'DELETE|/logout|||UNEXPECTED|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||',
                                                  'DELETE|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||',
                                                  'DELETE|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$nonexist_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||',
                                                  'DELETE|/logout|||200|{"okay":true}||||||||||||UNEXPECTED||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||'])    
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
        verdict,variable_value_dict=to_obj.runTC(tc, [], new_ts, constants.STEPS_SUP_EXE_FLC_VER_CLU, {}, s,[])
        pass
        if c_QATCPARAMSTEXT=='DELETE|/logout|||200|{"okay":true}||||||||||||||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||':
            assert verdict == [(constants.SUCCESS,'Success: status code expected and first level check succeed. No verification is done.')]
        if c_QATCPARAMSTEXT=='DELETE|/logout|||200|{"okay":true}||||||||||||login|||||||||||||||||||||||||||||||||':
            assert verdict==[(constants.SUCCESS,'Success: status code expected and first level check succeed. No verification is done.')]
        if c_QATCPARAMSTEXT=='DELETE|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","wrong_key":"$admin_password"}|||||||||||||||||||||||||||||||':
            assert verdict == [(constants.BLOCKED, 'Blocked: the test case is blocked because the test setup failed')]
        if c_QATCPARAMSTEXT=='DELETE|/logout|||200|{"okay":true}||||||||||||login||{"wrong_user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||':
            assert verdict==[(constants.BLOCKED, 'Blocked: the test case is blocked because the test setup failed')]
        if c_QATCPARAMSTEXT=='DELETE|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$nonexist_password"}|||||||||||||||||||||||||||||||':
            assert verdict==[(constants.BLOCKED, 'Blocked: the test case is blocked because the test setup failed')]
        if c_QATCPARAMSTEXT=='DELETE|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$nonexist_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||':
            assert verdict==[(constants.BLOCKED, 'Blocked: the test case is blocked because the test setup failed')]
        if c_QATCPARAMSTEXT=='DELETE|/logout|||200|{"okay":true}||||||||||||UNEXPECTED||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||':
            assert verdict==[(constants.BLOCKED, 'Blocked: the test case is blocked because the test setup failed')]
        if c_QATCPARAMSTEXT=='DELETE|/logout|||200|{"okay":false}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||':
            assert verdict==[(constants.FAILED, u"Failure: status code expected but first level check failed. Error: 'okay' : True in content of response is different from the expected.")]
        if c_QATCPARAMSTEXT=='NONEXIST|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||':
            assert verdict==[(constants.BLOCKED,'Blocked: the test case is blocked because the restful api call failed to run')]
        if c_QATCPARAMSTEXT=='DELETE|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||':
            assert verdict==[(constants.SUCCESS,'Success: status code expected and first level check succeed. No verification is done.')]
        if c_QATCPARAMSTEXT=='DELETE|/nonexist|||200|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||':
            assert verdict==[(constants.FAILED, 'Failure: status code unexpected. The unexpected status code of the response is 404')]              
        if c_QATCPARAMSTEXT=='DELETE|/logout|||UNEXPECTED|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||':
            assert verdict==[(constants.BLOCKED, 'Blocked: status code is expected to be digits instead of something else: UNEXPECTED')]           


    @pytest.mark.parametrize("c_QATCPARAMSTEXT", ['POST|/login||user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST||{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  '|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]||{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',                                                  
                                                  'POST|/login|{"user[email]":"$nonexist_email","user[password]":"nonexist_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login||user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"$admin_email"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"wrong_key":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||UNEXPECTED|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}||||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}||200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$nonexist_email"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"UNEXPECTED":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":false,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|UNEXPECTED|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/nonexist|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'NONEXIST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||',
                                                  'POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||'])    
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
        verdict,variable_value_dict=to_obj.runTC(tc, [], new_ts, constants.STEPS_SUP_EXE_FLC_VER_CLU, {}, s,[])
        #pass
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]||{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.BLOCKED,u'Blocked: status code is expected to be digits instead of something else: ')]
        if c_QATCPARAMSTEXT=='POST|/login||user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.BLOCKED,'Blocked: the test case is blocked because the restful api call failed to run')]
        if c_QATCPARAMSTEXT=='POST||{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.BLOCKED,'Blocked: the test case is blocked because the restful api call failed to run')]
        if c_QATCPARAMSTEXT=='|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.BLOCKED,'Blocked: the test case is blocked because the restful api call failed to run')]
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$nonexist_email","user[password]":"nonexist_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,'Failure: status code unexpected. The unexpected status code of the response is 401')]
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$admin_email"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,'Failure: status code unexpected. The unexpected status code of the response is 401')]
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,'Failure: status code unexpected. The unexpected status code of the response is 401')] 
        if c_QATCPARAMSTEXT=='POST|/login|{"wrong_key":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,'Failed: the test case failed because execution step failed')]
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||UNEXPECTED|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,'Failure: verification failed. Error: the api level test case name UNEXPECTED cannot be found in API test set TS1103')]
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}||||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,'Failure: verification failed. Error: the api level test case GetCurrentUser is Blocked: id, email, role is/are not defined in extra.json or pre-defined local variables')]
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,'Failure: verification failed. Error: the api level test case GetCurrentUser is Blocked: role is/are not defined in extra.json or pre-defined local variables')]
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}||200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.BLOCKED,'Blocked: user[email] is/are not defined in extra.json or pre-defined local variables')]
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$nonexist_email"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,u"Failure: status code expected but first level check failed. Error: 'email' : admin@spirent.com in content of response is different from the expected.")]
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"UNEXPECTED":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,u"Failure: status code expected but first level check failed. Error: 'UNEXPECTED' : {u'email': u'admin@spirent.com'} is missing from content of response.")]
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":false,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,"Failure: status code expected but first level check failed. Error: 'okay' : True in content of response is different from the expected.")]
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|UNEXPECTED|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.BLOCKED,'Blocked: status code is expected to be digits instead of something else: UNEXPECTED')]         
        if c_QATCPARAMSTEXT=='POST|/nonexist|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,'Failure: status code unexpected. The unexpected status code of the response is 404')]        
        if c_QATCPARAMSTEXT=='POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.SUCCESS,'Success: status code expected and first level check succeed. Verification is successful.')]
        if c_QATCPARAMSTEXT=='NONEXIST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||':
            assert verdict == [(constants.BLOCKED,'Blocked: the test case is blocked because the restful api call failed to run')]     


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
        with pytest.raises(Exception) as excinfo:
            to_obj.runTC(tc, [], new_ts, constants.STEPS_SUP_EXE_FLC_VER_CLU, {}, s,[])
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
        verdict,variable_value_dict=to_obj.runTC(tc, [], new_ts, constants.STEPS_SUP_EXE_FLC_VER_CLU, {}, s,[])
        #pass
        if c_QATCPARAMSTEXT=='POST|/users|{"user[email]":"$standard_email","user[firstname]":"$standard_firstname","user[lastname]":"$standard_lastname","user[role]":"$standard_role","user[password]":"$standard_password"}|user[email];UNEXPECTED;user[lastname]|200|{"firstname":"$user[firstname]","lastname":"$user[lastname]","email":"$user[email]"}|id;role;firstname;lastname;email|||GetUser|||DeleteUser;logout|||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}||||||||||||||||||||||||||||||':
            assert verdict == [(constants.FAILED,'Failed: the test case failed because execution step failed')]
        if c_QATCPARAMSTEXT=='POST|/users|{"user[email]":"$standard_email","user[firstname]":"$standard_firstname","user[lastname]":"$standard_lastname","user[role]":"$standard_role","user[password]":"$standard_password"}||200|{"firstname":"$user[firstname]","lastname":"$user[lastname]","email":"$user[email]"}|id;role;firstname;lastname;email|||GetUser|||DeleteUser;logout|||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}||||||||||||||||||||||||||||||':
            assert verdict == [(constants.BLOCKED,u'Blocked: user[firstname], user[lastname] is/are not defined in extra.json or pre-defined local variables')]
        if c_QATCPARAMSTEXT=='POST|/users|{"user[email]":"$standard_email","user[firstname]":"$standard_firstname","user[lastname]":"$standard_lastname","user[role]":"$standard_role","user[password]":"$standard_password"}|user[email];user[lastname]|200|{"firstname":"$user[firstname]","lastname":"$user[lastname]","email":"$user[email]"}|id;role;firstname;lastname;email|||GetUser|||DeleteUser;logout|||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}||||||||||||||||||||||||||||||':
            assert verdict == [(constants.BLOCKED,'Blocked: user[firstname] is/are not defined in extra.json or pre-defined local variables')]
        if c_QATCPARAMSTEXT=='POST|/users|{"user[email]":"$standard_email","user[firstname]":"$standard_firstname","user[lastname]":"$standard_lastname","user[role]":"$standard_role","user[password]":"$standard_password"}|user[email];user[firstname];user[lastname]|200|{"firstname":"$user[firstname]","lastname":"$user[lastname]","email":"$user[email]"}|id;role;firstname;lastname;email|||GetUser|||DeleteUser;logout|||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}||||||||||||||||||||||||||||||':
            assert verdict == [(constants.SUCCESS,'Success: status code expected and first level check succeed. Verification is successful.')]


   
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