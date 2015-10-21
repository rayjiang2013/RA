'''
Created on Jan 20, 2015

@author: ljiang
'''

import pytest
import sys
import os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from testSet import testSet
from copy import deepcopy
from testObject import testObject
from test_fixture_base import test_config_module    
        
#Test testObject/runTO
class TestTOrunTS:
    @pytest.fixture(scope="class",params=['TS484'])#unit test not working yet need update
    def config_class(self,test_config_module,request):
        print ("setup_class    class:%s" % self.__class__.__name__)
        #global ts_obj,ts,tcs,fids,new_self_data,ts_new
        (rally,data)=test_config_module
        data_to_runts=deepcopy(data) #use deepcopy instead of shallow one to create two separate object
        data_to_runts['ts']['FormattedID']=request.param
        #create to_obj
        to_obj=testObject(rally,data_to_runts)
        
        ts_obj=testSet(rally,data_to_runts)
        
        #(verd,new_self_data)=to_obj.runTO(ts_new)
        #(verd,new_data)=config_module[0].runTO(ts_new)
        #global new_self_data
        #new_self_data=deepcopy(data) #use deepcopy instead of shallow one to create two separate object
        #new_self_data['ts']['FormattedID']=ts_new.FormattedID
        
        def fin():
            print ("teardown_class class:%s" % self.__class__.__name__)
            #ts_new_obj=testSet(rally,new_self_data)
            #ts_new_obj.delTS()
            
        request.addfinalizer(fin)
        
        return (to_obj,ts_obj)#verd,new_data)      
            
    @pytest.mark.parametrize("verd", [[(0,'Failure: failure reason 1'),(1,'Success: success reason 1'),(2,'Blocked: blocked reason 1'),(3,"")]])  
    def test_testobject_runts_same_verdicts(self,config_class,verd):
        print 'test_testobject_runts_same_verdicts  <============================ actual test code'
        (to_obj,ts_obj)=config_class
        trs=to_obj.runTS(verd,ts_obj.data) 
        for tr,v in zip(trs,verd):
            if v[0]==0:
                assert tr.Verdict=='Fail'
            elif v[0]==1:
                assert tr.Verdict=='Pass'
            elif v[0]==2:
                assert tr.Verdict=='Blocked'
            else:
                assert tr.Verdict=='Error'
                