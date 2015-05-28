from src.test.run.testObject import testObject
import pytest
import sys


from pyral import Rally,rallyWorkset #The bugs  https://github.com/RallyTools/RallyRestToolkitForPython/issues/37 and https://github.com/RallyTools/RallyRestToolkitForPython/issues/40 should be fixed according comments from the po. Switch back to Pyral from now on.
#from pyrallei import Rally, rallyWorkset #By using custom package pyrallei as a workaround for the bug: bug: https://github.com/RallyTools/RallyRestToolkitForPython/issues/37
import json

import os
from copy import deepcopy

#pytest fixture example
@pytest.fixture(scope="module")
def test_config_module(request):
    try:
        #global rally,data,to_obj
        print ("setup_module      module:%s" % __name__)
        parent_path=os.path.dirname(os.path.dirname(__file__))
        options = ['--config='+parent_path+'/config.cfg'] #--config=config.cfg "extra.cfg"
        server, user, password, apikey, workspace, project = rallyWorkset(options) #apikey can be obtained from https://rally1.rallydev.com/login/
        #global rally
        rally = Rally(server, user, password, apikey=apikey,workspace=workspace, project=project)#include apikey=apikey to workaround http://stackoverflow.com/questions/30495164/getting-error-rallyrestapierror-422-not-authorized-to-perform-action-invalid and http://stackoverflow.com/questions/30492008/net-rally-restapi-error-not-authorized-to-perform-action-invalid-key-when-cr
        rally.enableLogging('rally.example.log', attrget=True, append=True)
        #global data
        # Read other configuration parameters from the extra.json
        with open(parent_path+'/extra.json') as data_file:    
            data = json.load(data_file)
        #global to_obj      
        #to_obj=testObject(rally,data)
        
        def fin():
            print "teardown_module      module:%s" % __name__
        request.addfinalizer(fin)
        
        return rally,data
    except Exception,details:
        
        print details
        sys.exit(1)



        
        