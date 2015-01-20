from src.test.run.testObject import testObject
from src.test.run.testSet import testSet
from src.test.run.testCaseResult import testCaseResult
from copy import deepcopy
#import src.test.run.example
import pytest
import sys

from pyrallei import Rally, rallyWorkset #By using custom package pyrallei as a workaround for the bug: bug: https://github.com/RallyTools/RallyRestToolkitForPython/issues/37
import json
import inspect
import datetime

#pytest fixture example
@pytest.fixture(scope="module")
def config_module(request):
    try:
        #global rally,data,to_obj
        print ("setup_module      module:%s" % __name__)
        options = ['--config=../config.cfg'] #--config=config.cfg "extra.cfg"
        server, user, password, apikey, workspace, project = rallyWorkset(options) #apikey can be obtained from https://rally1.rallydev.com/login/
        #global rally
        rally = Rally(server, user, password, workspace=workspace, project=project)
        rally.enableLogging('rally.example.log', attrget=True, append=True)
        #global data
        # Read other configuration parameters from the extra.json
        with open('../extra.json') as data_file:    
            data = json.load(data_file)
        #global to_obj
        to_obj=testObject(rally,data)
        
        def fin():
            print "teardown_module      module:%s" % __name__
        request.addfinalizer(fin)
        
        return (to_obj,rally,data)
    except Exception,details:
        
        print details
        sys.exit(1)

'''    
def teardown_module(module):
    try:
        ts_obj=testSet(rally,data)
        ts_obj.delTS()
    except Exception,details:
        
        print details
        sys.exit(1)
'''
#Test testObject/copyTS
class TestTOCopyTS:
    @pytest.fixture(scope="class")
    def config_class(self,config_module,request):
        try:
            print ("setup_class    class:%s" % self.__class__.__name__)
            #global ts_obj,ts,tcs,fids,new_self_data,ts_new
            (to_obj,rally,data)=config_module
            
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


    '''
    @pytest.fixture(scope="function")
    def config_method(self,config_module,request):
        try:
            print ("setup_method    method:%s" % self.config_method.__name__)
            #global ts_obj,ts,tcs,fids,new_self_data,ts_new
            
            ts_obj=testSet(config_module[1],config_module[2])
            ts=ts_obj.getTSByID()[0]
            tcs=ts_obj.allTCofTS(ts)
    
            fids=[]
            for tc in tcs:
                fids.append(tc.FormattedID)
            
            ts_new=config_module[0].copyTS()
            #global new_self_data
            new_self_data=deepcopy(config_module[2]) #use deepcopy instead of shallow one to create two separate object
            new_self_data['ts']['FormattedID']=ts_new.FormattedID
            
            def fin():
                try:
                    print ("teardown_method method:%s" % self.config_method.__name__)
                    ts_new_obj=testSet(config_module[1],new_self_data)
                    ts_new_obj.delTS()
            
                except Exception,details:
                    
                    print details
                    sys.exit(1)    
                    
            request.addfinalizer(fin)
            
            return (ts_new,ts,fids)
        except Exception,details:
            
            print details
            sys.exit(1)    
    
    
    def test_testobject_copyts_equal_formattedid():
        
        ts_new=to_obj.copyTS()   
        assert ts_new.FormattedID==data["ts"]["FormattedID"]  
    '''    
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
        
        
        
#Test testObject/runTO
class TestTOrunTO:
    @pytest.fixture(scope="class")
    def config_class(self,config_module,request):
        try:
            print ("setup_class    class:%s" % self.__class__.__name__)
            #global ts_obj,ts,tcs,fids,new_self_data,ts_new
            (to_obj,rally,data)=config_module
            ts_obj=testSet(rally,data)
            ts=ts_obj.getTSByID()[0]
            tcs=ts_obj.allTCofTS(ts)
    
            fids=[]
            for tc in tcs:
                fids.append(tc.FormattedID)
            
            ts_new=to_obj.copyTS()
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
            
            return (ts_new,ts,fids,new_self_data)#verd,new_data)
        except Exception,details:
            
            print details
            sys.exit(1)            


    @pytest.fixture(scope="function")
    def add_block_tr(self,config_module,config_class,request):
        try:
            print ("setup_method    method:%s" % inspect.stack()[0][3])
            (ts_new,ts,fids,new_self_data)=config_class
            rally=config_module[1]
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


    def test_testobject_runto_equal_formattedid(self,config_class,config_module):
        print 'test_testobject_runto_equal_formattedid  <============================ actual test code'
        to_obj=config_module[0]
        ts_new=config_class[0]
        new_data=(to_obj.runTO(ts_new))[1]
        assert ts_new.FormattedID==new_data['ts']['FormattedID']
        
    def test_testobject_runto_same_verdict_size(self,config_class,config_module):
        print 'test_testobject_runto_same_verdict_size  <============================ actual test code'
        to_obj=config_module[0]
        ts_new=config_class[0]
        verd=(to_obj.runTO(ts_new))[0]
        assert len(ts_new.TestCases)==len(verd)
        
    def test_testobject_runto_blocked(self,config_class,add_block_tr,config_module):
        print 'test_testobject_runto_blocked  <============================ actual test code'
        to_obj=config_module[0]
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
    
    def test_testobject_runto_state_in_process(self,config_class,config_module):
        print 'test_testobject_runto_state_in_process  <============================ actual test code'
        to_obj,rally=config_module[0:2]
        ts_new=config_class[0]
        data_new=to_obj.runTO(ts_new)[1]
        ts_obj=testSet(rally,data_new)
        ts_after_runTO=ts_obj.getTSByID()[0]
        assert ts_after_runTO.ScheduleState=="In-Progress"
        
        