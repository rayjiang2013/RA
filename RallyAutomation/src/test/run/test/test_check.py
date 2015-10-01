import sys
import os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pytest
from check import check
from test_fixture_base import test_config_module
class TestCheck:

    @pytest.fixture(scope="class")
    def config_class(self, request, test_config_module):
        print "setup_class    class:%s" % self.__class__.__name__
        (rally,data)=test_config_module
        check_obj=check(data,rally)
        def fin():
            print "teardown_class class:%s" % self.__class__.__name__
        request.addfinalizer(fin)
        return check_obj

    #check current license and license server should still be working
    def test_check_lic(self, config_class):
        return_value = config_class.checkLic(config_class.data['ts']['FormattedID'])
        assert return_value == True

    #ping devices and see if they are responsive
    @pytest.mark.parametrize("target, expected", [(['10.10.2.166', '10.10.3.107', '10.10.2.59',
                                                  '10.10.3.208', 'rally1.rallydev.com',
                                                  'localhost'], ''),
                                                  (['10.10.2.166'], ''),
                                                  (['10.10.3.107'], ''),
                                                  (['10.10.2.59'], ''),
                                                  (['10.10.3.208'], ''),
                                                  (['rally1.rallydev.com'], ''),
                                                  (['localhost'], '')])
    def test_ping(self, config_class, target, expected):
        return_value = config_class.ping(config_class.data['ts']['FormattedID'], *target)
        assert return_value == expected

    #negative ping tests
    @pytest.mark.parametrize("target, expected", [(['nonexist'], 'ping: cannot resolve nonexist: Unknown host'),
                                                  (['127.0.0.2'], 'Request timeout for 127.0.0.2')
                                                  ])
    def test_negative_ping(self, config_class, target, expected):
        with pytest.raises(Exception) as excinfo:
            config_class.ping(config_class.data['ts']['FormattedID'], *target)   
        assert expected in excinfo.value.message             
        