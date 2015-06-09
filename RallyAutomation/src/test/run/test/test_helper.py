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
    def test_testobject_append_local_variable_dict_to_variable_value_dict(self,config_class,search_path_list,variable_value_dict,local_variable_dict,current_api_call,return_value):
        print 'test_testobject_list_to_dict  <============================ actual test code'                         
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
    def test_testobject_searchDict3(self,config_class,d1,d2,error_message):
        print 'test_testobject_runtc_searchDict3  <============================ actual test code'                         
        helper_obj=config_class
        verdict=helper_obj.searchDict3(d1, d2, "")
        assert verdict == error_message

    @pytest.mark.parametrize("lst,return_value", [([{'i': 'j', 'k': [{'n': 'o'}, {'l': ['m', 'r']}, {'p': 'q'}], 'f': 'g'}, {'s': 't'}],{'1': {'s': 't'}, '0': {'i': 'j', 'k': {'1': {'l': {'1': 'r', '0': 'm'}}, '0': {'n': 'o'}, '2': {'p': 'q'}}, 'f': 'g'}})])
    def test_testobject_list_to_dict(self,config_class,lst,return_value):
        print 'test_testobject_list_to_dict  <============================ actual test code'                         
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
    def test_testobject_remove_number_key_of_dict(self,config_class,dt,return_value):
        print 'test_testobject_remove_number_key_of_dict  <============================ actual test code'                         
        helper_obj=config_class
        verdict=helper_obj.remove_number_key_of_dict(dt)
        assert verdict == return_value