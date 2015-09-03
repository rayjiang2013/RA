import pytest
from src.test.run.check import check
from test_fixture_base import test_config_module
class TestCheck:
    
    @pytest.fixture(scope="class")
    def config_class(self,request,test_config_module):
        print ("setup_class    class:%s" % self.__class__.__name__)
        (rally,data)=test_config_module
        check_obj=check(data,rally)
        
        def fin():
            print ("teardown_class class:%s" % self.__class__.__name__)
                
        request.addfinalizer(fin)
        
        return check_obj
    
    #check current license and license server should still be working
    def test_check_lic(self,config_class):
        return_value=config_class.checkLic(config_class.data['ts']['FormattedID'])
        assert return_value==True
        
        
        