'''
Created on Jan 20, 2015

@author: ljiang
'''
import pytest
from src.test.run.testSet import testSet
from src.test.run.testObject import testObject
from copy import deepcopy
import sys
import inspect

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
            
            ts_new=to_obj.copyTS()[0]
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


    @pytest.fixture(scope="function")
    def config_test_testobject_copyts_non_existed_ts_negative(self,test_config_module,request):
        try:
            print ("setup_function    function:%s" % inspect.stack()[0][3])
            #global ts_obj,ts,tcs,fids,new_self_data,ts_new
            (rally,data)=test_config_module[1:3]
            
            ts_obj=testSet(rally,data)
            ts=ts_obj.getTSByID()[0]
            tcs=ts_obj.allTCofTS(ts)
    
            fids=[]
            for tc in tcs:
                fids.append(tc.FormattedID)
            '''
            ts_new=to_obj.copyTS()
            #global new_self_data
            new_self_data=deepcopy(data) #use deepcopy instead of shallow one to create two separate object
            new_self_data['ts']['FormattedID']=ts_new.FormattedID
            '''
            def fin():
                try:
                    print ("teardown_function function:%s" % inspect.stack()[0][3])
                    '''
                    ts_new_obj=testSet(rally,new_self_data)
                    ts_new_obj.delTS()
                    '''
                except Exception,details:
                    
                    print details
                    sys.exit(1)    
                    
            request.addfinalizer(fin)
            
            return (ts,fids)
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

    @pytest.mark.parametrize("FormattedID", ['TS10000000','TS0'])        
    def test_testobject_copyts_non_existed_ts_negative(self,config_test_testobject_copyts_non_existed_ts_negative,test_config_module,FormattedID):
        print 'test_testobject_copyts_non_existed_ts_negative  <============================ actual test code'
        rally=test_config_module[1]
        new_data_with_non_existed_ts=deepcopy(test_config_module[2])
        new_data_with_non_existed_ts['ts']['FormattedID']=FormattedID
        to_obj=testObject(rally,new_data_with_non_existed_ts)
        
        with pytest.raises(Exception): #as excinfo:
            to_obj.copyTS()
        #assert "local variable" in excinfo.value     
