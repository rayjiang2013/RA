'''
Created on Jan 20, 2015

@author: ljiang
'''
import pytest
from src.test.run.testSet import testSet
from copy import deepcopy
import sys

from test_fixture_base import test_config_module

#Test testObject/copyTS
class TestTOCopyTS:
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
            
            ts_new=to_obj.copyTS()
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
            
            return (ts_new,ts,fids)
        except Exception,details:
            
            print details
            sys.exit(1)            

 
    def test_testobject_copyts_same_tc_order(self,config_class):
        print 'test_testobject_copyts_same_tc_order  <============================ actual test code'
        (ts_new,fids)=(config_class[0],config_class[2])
        tcs=ts_new.TestCases
        for tc in tcs:
            assert tc.FormattedID==fids[tcs.index(tc)]
    
    def test_testobject_copyts_same_ts_name(self,config_class):
        print 'test_testobject_copyts_same_ts_name  <============================ actual test code'
        (ts_new,ts)=config_class[0:2]
        assert ts_new.Name==ts.Name
    
    def test_testobject_copyts_defined_state(self,config_class):
        print 'test_testobject_copyts_defined_state  <============================ actual test code'
        ts_new=config_class[0]
        assert ts_new.ScheduleState=="Defined"
        