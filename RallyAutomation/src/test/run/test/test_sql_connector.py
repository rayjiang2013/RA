'''
To test class sqlConnector
'''
import pytest
import os
import sys
import json
from src.test.run.sqlConnector import sqlConnector

class TestSqlConnector:
    @pytest.fixture(scope="class",params=['/mysql.json'])
    def config_class(self,request):
        try:
            print ("setup_class    class:%s" % self.__class__.__name__)
            parent_path=os.path.dirname(os.path.dirname(__file__))
            config_file=parent_path+request.param
            with open(config_file) as mysql_data:
                mysql_data=json.load(mysql_data)
            sql_obj=sqlConnector(config_file,mysql_data)
            
            def fin():
                try:
                    print ("teardown_class class:%s" % self.__class__.__name__)
            
                except Exception,details:
                    
                    print details
                    sys.exit(1)    
                    
            request.addfinalizer(fin)
            
            return sql_obj
        except Exception,details:
            
            print details
            sys.exit(1)            

    @pytest.mark.parametrize("tc_name,tc_string",[('logout','DELETE|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||||||||||||||||||||||||||||||'),
                                                  ('login','POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout|||||||||||||||||||||||||||||||||||||'),
                                                  ('GetCurrentUser','GET|/current_user|||200|{"okay":true,"current_user":{"id":"$id","email":"$email","role":"$role"}}|||||||logout|||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}||||||||||||||||||||||||||||||')])
    #@pytest.fixture(scope="class",params=['ss'])
    def test_get_tcs_from_db(self,config_class,tc_name,tc_string):
        sql_obj=config_class
        assert sql_obj.getTCsFromDB(tc_name)==tc_string
        