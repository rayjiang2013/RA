'''
Created on Jun 9, 2015

@author: ljiang
'''
import pytest
from src.test.run.helper import helper
import sys
from test_fixture_base import test_config_module    

class TestHelper:
    
    @pytest.fixture(scope="class")
    def config_class(self,test_config_module,request):
        try:
            print ("setup_class    class:%s" % self.__class__.__name__)
            #global ts_obj,ts,tcs,fids,new_self_data,ts_new
            (rally,data)=test_config_module
            
            helper_obj=helper(rally,data)
            
            def fin():
                try:
                    print ("teardown_class class:%s" % self.__class__.__name__)
                    #ts_new_obj=testSet(rally,data_to_runto)
                    #ts_new_obj.delTS()
            
                except Exception,details:
                    
                    print details
                    sys.exit(1)    
                    
            request.addfinalizer(fin)
            
            return helper_obj
        except Exception,details:
            
            print details
            sys.exit(1)             
    
    

    @pytest.mark.parametrize("search_path_list,variable_value_dict,local_variable_dict,current_api_call,return_value", [(["Test Case Dummy","login","GetCurrentUser"],{"Test Case Dummy":{"login":{"GetCurrentUser":{"whatever":"whatever"}}}},{"whatever":"whatever"},"login",{'Test Case Dummy': {'login': {'GetCurrentUser': {'login': {'whatever': 'whatever'}, 'whatever': 'whatever'}}}})])
    def test_helper_append_local_variable_dict_to_variable_value_dict(self,config_class,search_path_list,variable_value_dict,local_variable_dict,current_api_call,return_value):
        print 'test_helper_append_local_variable_dict_to_variable_value_dict  <============================ actual test code'                         
        helper_obj=config_class
        
        verdict=helper_obj.append_local_variable_dict_to_variable_value_dict(search_path_list,variable_value_dict,local_variable_dict,current_api_call)
        assert verdict == return_value



    @pytest.mark.parametrize("d1,d2,error_message", [({"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"},{"l":"r"},{"p":"q"},{"n":"o"}]},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":[{"n":"o"},{"l":"m"}]}}," 'i' : j is missing from content of response. 'l' : r is missing from content of response. 'p' : q is missing from content of response."),
                                                     ({"a":"b","c":"d","e":[{"k":[{"l":"m"},{"l":"r"},{"p":"q"},{"n":"o"}],"f":"g","i":"j"},{"s":"t"}]},{"i":"j","a":"b","c":"d","e":{"f":"g","i":"j","k":[{"n":"o"},{"l":["m","r"]},{"p":"q"}]}}," 's' : t is missing from content of response."),
                                                     ({"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"},{"p":"q"},{"n":"o"}]},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":[{"n":"o"},{"l":"m"}]}}," 'i' : j is missing from content of response. 'p' : q is missing from content of response."),
                                                     ({"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"},{"n":"o"}]},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"}]}}," 'i' : j is missing from content of response. 'n' : o is missing from content of response."),
                                                     ({"a":"b","c":"d","e":{"f":"g","k":{"l":"m"}},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"}]}}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"}]},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"}]}}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","e":['f','g'],"i":"j"},{"a":"b","c":"d","e":['g']}," 'i' : j is missing from content of response. 'f' is missing from content of response."),
                                                     ({"a":"b","c":"d","e":[{"k":[{"l":"m"},{"l":"r"},{"p":"q"},{"n":"o"}],"f":"g","i":"j"},{"s":"t"}]},{"i":"j","c":"d","a":"b","e":[{"f":"g","i":"j","k":[{"n":"o"},{"l":["m","r"]},{"p":"q"}]},{"s":"t"}]},""),                                                     
                                                     ({"a":"b","c":"d","e":{"k":[{"l":"m"},{"l":"r"},{"p":"q"},{"n":"o"}],"f":"g","i":"j"}},{"i":"j","a":"b","c":"d","e":{"f":"g","i":"j","k":[{"n":"o"},{"l":["m","r"]},{"p":"q"}]}},""),
                                                     ({"a":"b","c":"d","e":{"k":[{"l":"m"},{"l":"r"},{"p":"q"},{"n":"o"}],"f":"g","i":"j"}},{"i":"j","a":"b","c":"d","e":{"f":"g","i":"j","k":[{"n":"o"},{"l":"m"},{"l":"r"},{"p":"q"}]}},""),
                                                     ({"a":"b","c":"d","e":{"k":[{"l":"m"},{"l":"r"},{"p":"q"},{"n":"o"}],"f":"g","i":"j"}},{"i":"j","a":"b","c":"d","e":{"f":"g","k":[{"n":"o"},{"l":"m"},{"l":"r"},{"p":"q"}]}}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","i":"j","e":{"k":[{"l":"m"},{"l":"r"},{"p":"q"},{"n":"o"}],"f":"g"}},{"a":"b","c":"d","e":{"f":"g","k":[{"n":"o"},{"l":"m"},{"l":"r"},{"p":"q"}]}}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"},{"l":"r"},{"p":"q"},{"n":"o"}]},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":[{"n":"o"},{"l":"m"},{"l":"r"},{"p":"q"}]}}," 'i' : j is missing from content of response."),                                                     
                                                     ({"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"},"p",{"n":"o"}]},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":[{"n":"o"},{"l":"m"}]}}," 'i' : j is missing from content of response. 'p' is missing from content of response."),
                                                     ({"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"},{"n":"o"}]},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":[{"n":"o"},{"l":"m"}]}}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"},]},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":[{"l":"m"}]}}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","e":{"f":"g","k":{"l":"m"}},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":"l"}}," 'i' : j is missing from content of response. 'k' : l in content of response is different from the expected."),
                                                     ({"a":"b","c":"d","e":{"f":"g","k":"l"},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":"l"}}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","e":{"f":"g"},"i":"j"},{"a":"b","c":"d","e":{"f":"g","k":"l"}}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","e":{"f":"g","k":"l"},"i":"j"},{"a":"b","c":"d","e":{"f":"g"}}," 'i' : j is missing from content of response. 'k' : l is missing from content of response."),
                                                     ({"a":"b","c":"d","e":{"f":"g"},"i":"j"},{"a":"b","c":"d","e":{"f":"g"}}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","e":"f","i":"j"},{"a":"b","c":"d","e":{"f":"g"}}," 'i' : j is missing from content of response. 'e' : {'f': 'g'} in content of response is different from the expected."),
                                                     ({"a":"b","c":"d","e":['f'],"i":"j"},{"a":"b","c":"d","e":['g']}," 'i' : j is missing from content of response. 'f' is missing from content of response. 'g' in content of response is different from the expected."),
                                                     ({"a":"b","c":"d","e":['f'],"i":"j"},{"a":"b","c":"d","e":['g']}," 'i' : j is missing from content of response. 'f' is missing from content of response. 'g' in content of response is different from the expected."),
                                                     ({"a":"b","c":"d","e":['f','g'],"i":"j"},{"a":"b","c":"d","e":['f','g','h']}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","e":[],"i":"j"},{"a":"b","c":"d","e":[]}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","e":"f","i":"j"},{"a":"b","c":"d","e":[]}," 'i' : j is missing from content of response. 'e' : [] in content of response is different from the expected."),
                                                     ({"a":"b","c":"d","e":"f","i":"j"},{"a":"b","c":"d","e":["f","k"]}," 'i' : j is missing from content of response."),
                                                     ({"a":"b","c":"d","e":"f","i":"j"},{"a":"b","c":"d","g":"h"}," 'i' : j is missing from content of response. 'e' : f is missing from content of response."),
                                                     ({"a":"b","c":"d","e":"f"},{"a":"b","c":"d","g":"h"}," 'e' : f is missing from content of response."),
                                                     ({"a":"b","c":"d"},{"a":"b","c":"d","e":"f"},""),({"a":"b","c":"d"},{"a":"b","c":"d"},""),
                                                     ({"a":"b","c":"d"},{"a":"b"}," 'c' : d is missing from content of response."),
                                                     ({},{},""),
                                                     ({"a":"b"},{"a":"b"},"")])
    def test_helper_searchDict3(self,config_class,d1,d2,error_message):
        print 'test_helper_searchDict3  <============================ actual test code'                         
        helper_obj=config_class
        verdict=helper_obj.searchDict3(d1, d2, "")
        assert verdict == error_message

    @pytest.mark.parametrize("lst,return_value", [([{'i': 'j', 'k': [{'n': 'o'}, {'l': ['m', 'r']}, {'p': 'q'}], 'f': 'g'}, {'s': 't'}],{'1': {'s': 't'}, '0': {'i': 'j', 'k': {'1': {'l': {'1': 'r', '0': 'm'}}, '0': {'n': 'o'}, '2': {'p': 'q'}}, 'f': 'g'}})])
    def test_helper_list_to_dict(self,config_class,lst,return_value):
        print 'test_helper_list_to_dict  <============================ actual test code'                         
        helper_obj=config_class
        verdict=helper_obj.list_to_dict(lst)
        assert verdict == return_value


    @pytest.mark.parametrize("dt,return_value", [({'0':{}},{}),
                                                 ({'1': {'i': 'j', 'k': {'1': {'n': 'o'}, '0': {'l': {'1': 'r', '0': 'm'}}, '2': {'p': 'q'}}, 'f': 'g'}, '0': {'s': 't'}},{'f': 'g', 'i': 'j', 'k': {'p': 'q', 'l': {'1': 'r', '0': 'm'}, 'n': 'o'}, 's': 't'}),
                                                 ({'1': {'l': 'r'}, '0': {'l': 'm'}, '3': {'p': {'0':{'q':'u'},'1':{'v':'w'},'2':{'q':'u'}}}, '2': {'n': 'o'},'5': 't', '4': {'l': 's'}},{'l': ['m', 'r', 's'], 'n': 'o', 'p': {'q': ['u','u'], 'v': 'w'}, '5': 't'}),
                                                 ({'1': {'l': 'r'}, '0': {'l': 'm'}, '3': {'p': 'q'}, '2': {'n': 'o'},'5': 't', '4': {'l': 'm'}},{'l': ['m', 'r','m'], 'p': 'q', 'n': 'o','5': 't'}),
                                                 ({'1': {'l': 'r'}, '0': {'l': 'm'}, '3': {'p': {'0':{'q':'u'},'1':{'v':'w'}}}, '2': {'n': 'o'},'5': 't', '4': {'l': 's'}},{'l': ['m', 'r', 's'], 'n': 'o', 'p': {'q': 'u', 'v': 'w'}, '5': 't'}),
                                                 ({'1': {'l': 'r'}, '0': {'l': 'm'}, '3': {'p': {'0':{'q':'u'}}}, '2': {'n': 'o'},'5': 't', '4': {'l': 's'}},{'l': ['m', 'r','s'], 'p': {'q':'u'}, 'n': 'o','5': 't'}),
                                                 ({'1': {'l': 'r'}, '0': {'l': 'm'}, '3': {'p': {'q':'u'}}, '2': {'n': 'o'},'5': 't', '4': {'l': 's'}},{'l': ['m', 'r','s'], 'p': {'q':'u'}, 'n': 'o','5': 't'}),
                                                 ({'1': {'l': 'r'}, '0': {'l': 'm'}, '3': {'p': 'q'}, '2': {'n': 'o'},'5': 't', '4': {'l': 's'}},{'l': ['m', 'r','s'], 'p': 'q', 'n': 'o','5': 't'}),
                                                 ({'1': {'l': 'r'}, '0': {'l': 'm'}, '3': {'p': 'q'}, '2': {'n': 'o'}, '4': {'l': 's'}},{'l': ['m', 'r','s'], 'p': 'q', 'n': 'o'}),
                                                 ({'1': {'l': 'r'}, '0': {'l': 'm'}, '3': {'p': 'q'}, '2': {'n': 'o'}},{'l': ['m', 'r'], 'p': 'q', 'n': 'o'})])
    def test_helper_remove_number_key_of_dict(self,config_class,dt,return_value):
        print 'test_helper_remove_number_key_of_dict  <============================ actual test code'                         
        helper_obj=config_class
        verdict=helper_obj.remove_number_key_of_dict(dt)
        assert verdict == return_value
        
    @pytest.mark.parametrize("search_dict, field,search_path_list,expected_return_value", [({u'av_devices': [{u'profile': u'L4L7-Functional', u'cpu': 0, u'av_port_groups': [{u'software': u'l4l7Vm4.51.1736', u'capacity': 40, u'av_queue': {u'capacity': 160, u'name': u'Alpha', u'_rev': u'3-59056cd963e413bb2234f53a08137016', u'av_port_group_ids': [u'86d185b614262931f61dc3908f1f4f74', u'86d185b614262931f61dc3908f1f3fc8', u'86d185b614262931f61dc3908f1f2661', u'86d185b614262931f61dc3908f1f0fb3'], u'range': {u'connections': {u'max': 1000000, u'min': 100}, u'connection_rate': {u'max': 150000, u'min': 1}, u'bandwidth': {u'max': 20000000000L, u'min': 1000000}, u'concurrency': {u'max': 1000000, u'min': 1}}, u'av_queue_test_ids': [], u'user_id': u'4e3462c5f03978eaee74332fea9a5b20', u'_id': u'9d413c90b7b52b27236c6590dd11bffb', u'type': u'AvQueue'}, u'av_ports': [{u'auto_negotiation': u'true', u'displayName': u'Eth0', u'duplex': u'Full Duplex', u'media': u'Fiber', u'vlan': {}, u'enabled': u'true', u'number': 1, u'routes': {u'ipv4': [], u'ipv6': []}, u'mac': u'', u'link': u'NONE', u'interface': {u'ipv4': {u'count': u'1000', u'addr_begin': u'101.0.0.1', u'addr_end': u'101.0.3.232', u'mask': u'16'}}, u'port_id': u'1', u'id': u'86d185b614262931f61dc3908f1f58d9', u'speed': u'10000'}, {u'auto_negotiation': u'true', u'displayName': u'Eth1', u'duplex': u'Full Duplex', u'media': u'Fiber', u'vlan': {}, u'enabled': u'true', u'number': 2, u'routes': {u'ipv4': [], u'ipv6': []}, u'mac': u'', u'link': u'NONE', u'interface': {u'ipv4': {u'count': u'1000', u'addr_begin': u'102.0.0.1', u'addr_end': u'102.0.3.232', u'mask': u'16'}}, u'port_id': u'2', u'id': u'86d185b614262931f61dc3908f1f55a4', u'speed': u'10000'}], u'memory': 31635000, u'cores': 4, u'group_id': u'1', u'id': u'86d185b614262931f61dc3908f1f4f74', u'reserve_state': u'Available'}, {u'software': u'l4l7Vm4.51.1736', u'capacity': 40, u'av_queue': {u'capacity': 160, u'name': u'Alpha', u'_rev': u'3-59056cd963e413bb2234f53a08137016', u'av_port_group_ids': [u'86d185b614262931f61dc3908f1f4f74', u'86d185b614262931f61dc3908f1f3fc8', u'86d185b614262931f61dc3908f1f2661', u'86d185b614262931f61dc3908f1f0fb3'], u'range': {u'connections': {u'max': 1000000, u'min': 100}, u'connection_rate': {u'max': 150000, u'min': 1}, u'bandwidth': {u'max': 20000000000L, u'min': 1000000}, u'concurrency': {u'max': 1000000, u'min': 1}}, u'av_queue_test_ids': [], u'user_id': u'4e3462c5f03978eaee74332fea9a5b20', u'_id': u'9d413c90b7b52b27236c6590dd11bffb', u'type': u'AvQueue'}, u'av_ports': [{u'auto_negotiation': u'true', u'displayName': u'Eth2', u'duplex': u'Full Duplex', u'media': u'Fiber', u'vlan': {}, u'enabled': u'true', u'number': 3, u'routes': {u'ipv4': [], u'ipv6': []}, u'mac': u'', u'link': u'NONE', u'interface': {u'ipv4': {u'count': u'1000', u'addr_begin': u'103.0.0.1', u'addr_end': u'103.0.3.232', u'mask': u'16'}}, u'port_id': u'3', u'id': u'86d185b614262931f61dc3908f1f4f73', u'speed': u'10000'}, {u'auto_negotiation': u'true', u'displayName': u'Eth3', u'duplex': u'Full Duplex', u'media': u'Fiber', u'vlan': {}, u'enabled': u'true', u'number': 4, u'routes': {u'ipv4': [], u'ipv6': []}, u'mac': u'', u'link': u'NONE', u'interface': {u'ipv4': {u'count': u'1000', u'addr_begin': u'104.0.0.1', u'addr_end': u'104.0.3.232', u'mask': u'16'}}, u'port_id': u'4', u'id': u'86d185b614262931f61dc3908f1f4e0c', u'speed': u'10000'}], u'memory': 31635000, u'cores': 4, u'group_id': u'3', u'id': u'86d185b614262931f61dc3908f1f3fc8', u'reserve_state': u'Available'}, {u'software': u'l4l7Vm4.51.1736', u'capacity': 40, u'av_queue': {u'capacity': 160, u'name': u'Alpha', u'_rev': u'3-59056cd963e413bb2234f53a08137016', u'av_port_group_ids': [u'86d185b614262931f61dc3908f1f4f74', u'86d185b614262931f61dc3908f1f3fc8', u'86d185b614262931f61dc3908f1f2661', u'86d185b614262931f61dc3908f1f0fb3'], u'range': {u'connections': {u'max': 1000000, u'min': 100}, u'connection_rate': {u'max': 150000, u'min': 1}, u'bandwidth': {u'max': 20000000000L, u'min': 1000000}, u'concurrency': {u'max': 1000000, u'min': 1}}, u'av_queue_test_ids': [], u'user_id': u'4e3462c5f03978eaee74332fea9a5b20', u'_id': u'9d413c90b7b52b27236c6590dd11bffb', u'type': u'AvQueue'}, u'av_ports': [{u'auto_negotiation': u'true', u'displayName': u'Eth4', u'duplex': u'Full Duplex', u'media': u'Fiber', u'vlan': {}, u'enabled': u'true', u'number': 5, u'routes': {u'ipv4': [], u'ipv6': []}, u'mac': u'', u'link': u'NONE', u'interface': {u'ipv4': {u'count': u'1000', u'addr_begin': u'105.0.0.1', u'addr_end': u'105.0.3.232', u'mask': u'16'}}, u'port_id': u'5', u'id': u'86d185b614262931f61dc3908f1f3c50', u'speed': u'10000'}, {u'auto_negotiation': u'true', u'displayName': u'Eth5', u'duplex': u'Full Duplex', u'media': u'Fiber', u'vlan': {}, u'enabled': u'true', u'number': 6, u'routes': {u'ipv4': [], u'ipv6': []}, u'mac': u'', u'link': u'NONE', u'interface': {u'ipv4': {u'count': u'1000', u'addr_begin': u'106.0.0.1', u'addr_end': u'106.0.3.232', u'mask': u'16'}}, u'port_id': u'6', u'id': u'86d185b614262931f61dc3908f1f34f3', u'speed': u'10000'}], u'memory': 31635000, u'cores': 4, u'group_id': u'5', u'id': u'86d185b614262931f61dc3908f1f2661', u'reserve_state': u'Available'}, {u'software': u'l4l7Vm4.51.1736', u'capacity': 40, u'av_queue': {u'capacity': 160, u'name': u'Alpha', u'_rev': u'3-59056cd963e413bb2234f53a08137016', u'av_port_group_ids': [u'86d185b614262931f61dc3908f1f4f74', u'86d185b614262931f61dc3908f1f3fc8', u'86d185b614262931f61dc3908f1f2661', u'86d185b614262931f61dc3908f1f0fb3'], u'range': {u'connections': {u'max': 1000000, u'min': 100}, u'connection_rate': {u'max': 150000, u'min': 1}, u'bandwidth': {u'max': 20000000000L, u'min': 1000000}, u'concurrency': {u'max': 1000000, u'min': 1}}, u'av_queue_test_ids': [], u'user_id': u'4e3462c5f03978eaee74332fea9a5b20', u'_id': u'9d413c90b7b52b27236c6590dd11bffb', u'type': u'AvQueue'}, u'av_ports': [{u'auto_negotiation': u'true', u'displayName': u'Eth6', u'duplex': u'Full Duplex', u'media': u'Fiber', u'vlan': {}, u'enabled': u'true', u'number': 7, u'routes': {u'ipv4': [], u'ipv6': []}, u'mac': u'', u'link': u'NONE', u'interface': {u'ipv4': {u'count': u'1000', u'addr_begin': u'107.0.0.1', u'addr_end': u'107.0.3.232', u'mask': u'16'}}, u'port_id': u'7', u'id': u'86d185b614262931f61dc3908f1f2595', u'speed': u'10000'}, {u'auto_negotiation': u'true', u'displayName': u'Eth7', u'duplex': u'Full Duplex', u'media': u'Fiber', u'vlan': {}, u'enabled': u'true', u'number': 8, u'routes': {u'ipv4': [], u'ipv6': []}, u'mac': u'', u'link': u'NONE', u'interface': {u'ipv4': {u'count': u'1000', u'addr_begin': u'108.0.0.1', u'addr_end': u'108.0.3.232', u'mask': u'16'}}, u'port_id': u'8', u'id': u'86d185b614262931f61dc3908f1f1d10', u'speed': u'10000'}], u'memory': 31635000, u'cores': 4, u'group_id': u'7', u'id': u'86d185b614262931f61dc3908f1f0fb3', u'reserve_state': u'Available'}], u'mode': u'NA', u'serial_number': u'7-324B20DB', u'model': u'SPT-C100-MP-3', u'device_id': u'1', u'id': u'86d185b614262931f61dc3908f1f057c', u'software': u'4.51.1736'}], u'capacity': 160, u'description': u'SPT-C100', u'ip': u'10.10.3.240', u'firmware': {u'version': u'4.51.6166', u'latest': False}, u'online': True, u'serial_number': u'7-324B20DB', u'total_slots': 1, u'id': u'10.10.3.240'},"id",[u'av_devices', [0], u'av_port_groups', [0, 1, 2, 3]],[[[u'86d185b614262931f61dc3908f1f4f74'], [u'86d185b614262931f61dc3908f1f3fc8'], [u'86d185b614262931f61dc3908f1f2661'], [u'86d185b614262931f61dc3908f1f0fb3']]])])    
    def test_helper_searchKeyInDic(self,config_class,search_dict, field,search_path_list,expected_return_value):
        print 'test_helper_searchKeyInDic  <============================ actual test code'                         
        helper_obj=config_class
        verdict=helper_obj.searchKeyInDic(search_dict, field,search_path_list)
        assert verdict == expected_return_value       
        