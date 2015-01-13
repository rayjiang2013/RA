from src.test.run.testObject import testObject
from src.test.run.testSet import testSet
#import src.test.run.example
#import pytest
import sys

from pyrallei import Rally, rallyWorkset #By using custom package pyrallei as a workaround for the bug: bug: https://github.com/RallyTools/RallyRestToolkitForPython/issues/37
import json


def setup_module(module):
    try:
        options = ['--config=../config.cfg'] #--config=config.cfg "extra.cfg"
        server, user, password, apikey, workspace, project = rallyWorkset(options) #apikey can be obtained from https://rally1.rallydev.com/login/
        global rally
        rally = Rally(server, user, password, workspace=workspace, project=project)
        rally.enableLogging('rally.example.log', attrget=True, append=True)
        global data
        # Read other configuration parameters from the extra.json
        with open('../extra.json') as data_file:    
            data = json.load(data_file)
        global to_obj
        to_obj=testObject(rally,data)
        
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
def setup_function(function):
    try:
        ts_obj=testSet(rally,data)
        ts=ts_obj.getTSByID()[0]
        tcs=ts_obj.allTCofTS(ts)
        global fids 
        fids=[]
        for tc in tcs:
            fids.append(tc.FormattedID)
    except Exception,details:
        
        print details
        sys.exit(1)    

def teardown_function(function):
    try:
        ts_obj=testSet(rally,new_self_data)
        ts_obj.delTS()
    except Exception,details:
        
        print details
        sys.exit(1)    

'''
def test_testobject_copyts_equal_formattedid():
    
    ts_new=to_obj.copyTS()   
    assert ts_new.FormattedID==data["ts"]["FormattedID"]  
'''    
def test_testobject_copyts_same_tc_order():
    ts_new=to_obj.copyTS()
    global new_self_data
    new_self_data=data.copy()
    new_self_data['ts']['FormattedID']=ts_new.FormattedID
    tcs=ts_new.TestCases
    for tc in tcs:
        assert tc.FormattedID==fids[tcs.index(tc)]

    