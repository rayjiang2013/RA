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
        
#Test testObject/runTO
class TestTOrunTO:
    @pytest.fixture(scope="class",params=['TS484'])
    def config_class(self,test_config_module,request):
        try:
            print ("setup_class    class:%s" % self.__class__.__name__)
            #global ts_obj,ts,tcs,fids,new_self_data,ts_new
            (rally,data)=test_config_module
            
            data_to_runto=deepcopy(data) #use deepcopy instead of shallow one to create two separate object
            data_to_runto['ts']['FormattedID']=request.param
            
            ts_obj=testSet(rally,data_to_runto)
            ts=ts_obj.getTSByID()[0]
                        
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
            ts_with_block=ts_obj.getTSByID()[0]
            
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
        (ts,to_obj,ts_obj)=config_class[0:3]
        to_obj.runTO(ts)[1]
        ts_after_runTO=ts_obj.getTSByID()[0]
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