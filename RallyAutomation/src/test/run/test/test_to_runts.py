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
        
#Test testObject/runTO
class TestTOrunTS:
    @pytest.fixture(scope="class")
    def config_class(self,test_config_module,request):
        try:
            print ("setup_class    class:%s" % self.__class__.__name__)
            #global ts_obj,ts,tcs,fids,new_self_data,ts_new
            (to_obj,rally,data)=test_config_module
            ts_obj=testSet(rally,data)
            ts=ts_obj.getTSByID()[0]
            tcs=ts_obj.allTCofTS(ts)
    
            fids=[]
            for tc in tcs:
                fids.append(tc.FormattedID)
            
            ts_new,tcs_objs=to_obj.copyTS()
            #(verd,new_self_data)=to_obj.runTO(ts_new)
            #(verd,new_data)=config_module[0].runTO(ts_new)
            #global new_self_data
            new_self_data=deepcopy(data) #use deepcopy instead of shallow one to create two separate object
            new_self_data['ts']['FormattedID']=ts_new.FormattedID
            
            def fin():
                try:
                    print ("teardown_class class:%s" % self.__class__.__name__)
                    ts_new_obj=testSet(rally,new_self_data)
                    ts_new_obj.delTS()
            
                except Exception,details:
                    
                    print details
                    sys.exit(1)    
                    
            request.addfinalizer(fin)
            
            return (ts_new,ts,fids,new_self_data,tcs_objs)#verd,new_data)
        except Exception,details:
            
            print details
            sys.exit(1)            
            
    @pytest.mark.parametrize("verd", [[(0,'Failure: failure reason 1'),(1,'Success: success reason 1'),(2,'Blocked: blocked reason 1'),(3,"")]])  
    def test_testobject_runts_same_verdicts(self,config_class,test_config_module,verd):
        print 'test_testobject_runts_other_verdicts_negative  <============================ actual test code'
        to_obj=test_config_module[0]
        new_self_data,tcs_objs=config_class[3],config_class[4]
        trs=to_obj.runTS(verd,new_self_data,tcs_objs) 
        for tr,v in zip(trs,verd):
            if v[0]==0:
                assert tr.Verdict=='Fail'
            elif v[0]==1:
                assert tr.Verdict=='Pass'
            elif v[0]==2:
                assert tr.Verdict=='Blocked'
            else:
                assert tr.Verdict=='Error'
                
    '''
    @pytest.fixture(scope="function")
    def add_block_tr(self,test_config_module,config_class,request):
        try:
            print ("setup_method    method:%s" % inspect.stack()[0][3])
            (ts_new,ts,fids,new_self_data)=config_class
            rally=test_config_module[1]
            tcr_data={"Build":new_self_data['ts']['Build'],
                      "Verdict":"Blocked",
                      "TestSet":ts_new._ref,
                      "TestCase":ts_new.TestCases[0]._ref,
                      'Date':datetime.datetime.now().isoformat()
                      }
            new_self_block_data=deepcopy(new_self_data)
            new_self_block_data['tcresult'].update(tcr_data)
            tcr_obj=testCaseResult(rally,new_self_block_data)
            tcr_block=tcr_obj.createTCResult()
            
            ts_obj=testSet(rally,new_self_block_data)
            ts_with_block=ts_obj.getTSByID()[0]
            def fin():
                try:
                    inspect_elements=inspect.stack()
                    print ("teardown_method method:%s" % inspect_elements[0][3])
                    new_self_block_data['tcresult'].update({"oid":tcr_block.oid})
                    ts_new_obj=testCaseResult(rally,new_self_block_data)
                    ts_new_obj.delTCR()
            
                except Exception,details:
                    
                    print details
                    sys.exit(1)    
                    
            request.addfinalizer(fin)
            
            return ts_with_block
        except Exception,details:
            
            print details
            sys.exit(1)    
    

    def test_testobject_runto_equal_formattedid(self,config_class,test_config_module):
        print 'test_testobject_runto_equal_formattedid  <============================ actual test code'
        to_obj=test_config_module[0]
        ts_new=config_class[0]
        new_data=(to_obj.runTO(ts_new))[1]
        assert ts_new.FormattedID==new_data['ts']['FormattedID']
        
    def test_testobject_runto_same_verdict_size(self,config_class,test_config_module):
        print 'test_testobject_runto_same_verdict_size  <============================ actual test code'
        to_obj=test_config_module[0]
        ts_new=config_class[0]
        verd=(to_obj.runTO(ts_new))[0]
        assert len(ts_new.TestCases)==len(verd)
        
    def test_testobject_runto_blocked(self,config_class,add_block_tr,test_config_module):
        print 'test_testobject_runto_blocked  <============================ actual test code'
        to_obj=test_config_module[0]
        ts_new=add_block_tr
        (verd,new_data)=to_obj.runTO(ts_new)
        tcs=ts_new.TestCases
        for v in verd:
            if v[0] == 2:
                sorted_trs=sorted(tcs[verd.index(v)].Results,key=lambda x: x.Date, reverse=True)
                same_build_tr_list=[]
                for tr in sorted_trs:
                    if new_data['ts']['Build']==tr.Build:
                        same_build_tr_list.append(tr)
                break
        assert same_build_tr_list[0].Verdict=="Blocked"
    
    def test_testobject_runto_state_in_process(self,config_class,test_config_module):
        print 'test_testobject_runto_state_in_process  <============================ actual test code'
        to_obj,rally=test_config_module[0:2]
        ts_new=config_class[0]
        data_new=to_obj.runTO(ts_new)[1]
        ts_obj=testSet(rally,data_new)
        ts_after_runTO=ts_obj.getTSByID()[0]
        assert ts_after_runTO.ScheduleState=="In-Progress"
    '''