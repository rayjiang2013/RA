'''
To test class sqlConnector
'''
import pytest
import os
import sys
import json
import inspect
from src.test.run.ssh import ssh
from src.test.run.sqlConnector import sqlConnector
from src.test.run.sqlFunctions import sql_functions

class TestSqlConnector:
    @pytest.fixture(scope="class",params=[('mysql.json','ssh.json')])
    def config_class(self,request):
        print ("setup_class    class:%s" % self.__class__.__name__)
        parent_path=os.path.dirname(os.path.dirname(__file__))
        config_file=parent_path+'/'+request.param[0]
        with open(config_file) as mysql_data:
            mysql_data=json.load(mysql_data)
        sql_obj=sqlConnector(config_file,mysql_data)
        
        #setup mysql session, create database under test
        sql_func_obj=sql_functions(config_file,'sqldb')
        queries="DROP DATABASE IF EXISTS %s_clone; create database %s_clone;" % (mysql_data['sqldb']['db'],mysql_data['sqldb']['db'])
        query_lst=queries.split(';')
        for query in query_lst:
            sql_func_obj.send_query(query)
        
        # Read ssh configuration parameters from the ssh.json; clone db 
        with open(parent_path+'/'+request.param[1]) as ssh_file:    
            ssh_data = json.load(ssh_file)            
        ssh_obj=ssh(ssh_data)
        connection=ssh_obj.setupConnection()
        stdin, stdout, stderr=ssh_obj.runCMD(connection,"mysqldump -h %s -u %s -p%s -d %s | mysql -h %s -u %s -p%s -D %s_clone"  
                       % (mysql_data['sqldb']['host'],mysql_data['sqldb']['user'],mysql_data['sqldb']['passwd'],mysql_data['sqldb']['db'],
                          mysql_data['sqldb']['host'],mysql_data['sqldb']['user'],mysql_data['sqldb']['passwd'],mysql_data['sqldb']['db']))
        #hold until stdout is returned
        while stdout.readlines()!=[]:
            if stderr.readlines()!=[]:
               raise Exception("".join(stderr.readlines())) 
            continue
        
        def fin():
            print ("teardown_class class:%s" % self.__class__.__name__)
            #need delete the schema cloned; also close ssh and mysql session
            ssh_obj.tearConnection(connection)
            drop_query="DROP DATABASE IF EXISTS %s_clone" % (mysql_data['sqldb']['db'])
            sql_func_obj.send_query(drop_query)
            sql_func_obj.end_connection()
                
        request.addfinalizer(fin)
        
        return sql_func_obj,sql_obj,ssh_obj,connection      
            
    @pytest.fixture(scope="class", params=[("INSERT INTO `softqadb_lei_clone`.`TestRunTestCase` (`TRTCID`, `TestCaseName`, `TR_TC_Cleanup`, `TR_TC_Execution`, `TR_TC_FLC`, `TR_TC_Verification`) VALUES ('1', 'login', 'logout||||', 'POST|/login|{\"user[email]\":\"$admin_email\",\"user[password]\":\"$admin_password\"}|user[email]', '200|{\"okay\":true,\"current_user\":{\"email\":\"$user[email]\"}}|role;id;email|', '||GetCurrentUser||');",
                                               "INSERT INTO `softqadb_lei_clone`.`TestRunTestCase` (`TRTCID`, `TestCaseName`, `TR_TC_Setup`, `TR_TC_Execution`, `TR_TC_FLC`, `TR_TC_Verification`) VALUES ('2', 'logout', 'login||{\"user[email]\":\"$admin_email\",\"user[password]\":\"$admin_password\"}||', 'DELETE|/logout||', '200|{\"okay\":true}||', '');",
                                               "INSERT INTO `softqadb_lei_clone`.`TestRunTestCase` (`TRTCID`, `TestCaseName`, `TR_TC_Cleanup`, `TR_TC_Setup`, `TR_TC_Execution`, `TR_TC_FLC`) VALUES ('3', 'GetCurrentUser', 'logout||||', 'login||{\"user[email]\":\"$admin_email\",\"user[password]\":\"$admin_password\"}||', 'GET|/current_user||', '200|{\"okay\":true,\"current_user\":{\"id\":\"$id\",\"email\":\"$email\",\"role\":\"$role\"}}||');")])
    def config_get_tcs_from_db(self,config_class,request):
        print ("setup_method    method: %s" % inspect.stack()[0][3])
        sql_func_obj,sql_obj,ssh_obj,connection=config_class
        for command in request.param:
            sql_func_obj.send_query(command)
        def fin():
            print ("teardown_method method: config_get_tcs_from_db")    
        request.addfinalizer(fin) 
        

    @pytest.mark.parametrize("tc_name,tc_string",[('logout','DELETE|/logout|||200|{"okay":true}||||||||||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||'),
                                                  ('login','POST|/login|{"user[email]":"$admin_email","user[password]":"$admin_password"}|user[email]|200|{"okay":true,"current_user":{"email":"$user[email]"}}|role;id;email|||GetCurrentUser|||logout||||||||||'),
                                                  ('GetCurrentUser','GET|/current_user|||200|{"okay":true,"current_user":{"id":"$id","email":"$email","role":"$role"}}|||||||logout|||||login||{"user[email]":"$admin_email","user[password]":"$admin_password"}|||')])
    #@pytest.fixture(scope="class",params=['ss'])
    def test_get_tcs_from_db(self,config_get_tcs_from_db,config_class,tc_name,tc_string):
        print 'test_get_tcs_from_db  <============================ actual test code'
        sql_func_obj,sql_obj,ssh_obj,connection=config_class
        assert sql_obj.getTCFromDB(tc_name)==tc_string
        