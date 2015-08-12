'''
Created on Aug 5, 2015

@author: jwerner
'''
import pytest
import json
import os
from src.test.run.mysqlConnection import sql_functions
import mysql.connector
import datetime


"""Opens A Working Connection To Test Functions Within"""
@pytest.fixture(scope='module',params=[("../mysql_test.json",'sqldb','../mysql.json')])
def class_instance_fixture(request):
    jfile,key,value_file = request.param
    with open(value_file) as json_data_file:
            data = json.load(json_data_file)
            data[key].pop('database',None)
    create_schema(data)
    data['sqldb']['database'] = 'UnitTest'
    with open(jfile,'w') as outfile:
        json.dump(data,outfile)
    class_instance_fixture = sql_functions(jfile,key)
    def fin():  
        class_instance_fixture.end_connection()
        os.remove(jfile)
        remove_schema(data)
    request.addfinalizer(fin)
    return(class_instance_fixture)

def create_schema(values): #creates a schema to be used for the unit tests
    queries = [
               "DROP SCHEMA IF EXISTS UnitTest;",
               "CREATE SCHEMA IF NOT EXISTS UnitTest DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;",
               "USE UnitTest;",
               "DROP TABLE IF EXISTS UserInfo;",
               "CREATE TABLE IF NOT EXISTS UserInfo (UserID INT NOT NULL AUTO_INCREMENT,Username VARCHAR(10) NULL,Password VARCHAR(10) NULL,PRIMARY KEY (UserID)) ENGINE = InnoDB;",
               "DROP TABLE IF EXISTS TestCases;",
               "CREATE TABLE IF NOT EXISTS TestCases (TCID INT NOT NULL,TimeRun DATETIME NULL,PRIMARY KEY (TCID)) ENGINE = InnoDB;",
               "DROP TABLE IF EXISTS Results;",
               "CREATE TABLE IF NOT EXISTS Results (PassFail TINYINT(1) NULL,FailReason VARCHAR(10) NULL) ENGINE = InnoDB;",
               "INSERT INTO UserInfo VALUES (1,'user1','pass1'),(2,'user2','pass2'),(3,'user3','pass3');",
               "INSERT INTO TestCases VALUES (1,'2012-12-12'),(2,'2013-12-12'),(3,'2014-12-12');",
               "INSERT INTO Results VALUES (0,'Network'),(1,NULL),(0,'Unknown');"
               ]
    cnx_info = values['sqldb']
    cnx = mysql.connector.connect(**cnx_info)
    cursor = cnx.cursor()
    for i in queries:
        cursor.execute(i)
    cnx.commit()
    cursor.close()
    cnx.close()

def remove_schema(values):
    cnx_info = values['sqldb']
    cnx = mysql.connector.connect(**cnx_info)
    cursor = cnx.cursor()
    cursor.execute('DROP SCHEMA IF EXISTS UnitTest;')

@pytest.fixture(scope = "function")
def reset_schema(request, class_instance_fixture):
    def reset(): 
        cursor = class_instance_fixture.cnx.cursor()
        queries = [
                   "TRUNCATE TABLE UserInfo;",
                   "TRUNCATE TABLE TestCases;",
                   "TRUNCATE TABLE Results;",
                   "INSERT INTO UserInfo VALUES (1,'user1','pass1'),(2,'user2','pass2'),(3,'user3','pass3');",
                   "INSERT INTO TestCases VALUES (1,'2012-12-12'),(2,'2013-12-12'),(3,'2014-12-12');",
                   "INSERT INTO Results VALUES (0,'Network'),(1,NULL),(0,'Unknown');"
                   ]
        for i in queries:
            cursor.execute(i)
    request.addfinalizer(reset)
"""Creates JSON Files to be Used in Unit Tests"""
@pytest.fixture(scope='function',params=[
                                       ("../bad_pass.json","../mysql.json",'sqldb')
                                       ])
def create_bad_pass_json_file(request):
    jfile,info_file,key = request.param
    with open(info_file) as json_data_file:
            data = json.load(json_data_file)
            data[key]['password'] = 'bad_pass'
    with open(jfile,'w') as outfile:
        json.dump(data,outfile)
    def fin():  
        os.remove(jfile)
    request.addfinalizer(fin)
    return jfile
@pytest.fixture(scope='function',params=[
                                       ("../bad_db.json","../mysql.json",'sqldb')
                                       ])
def create_bad_db_json_file(request):
    jfile,info_file,key = request.param
    with open(info_file) as json_data_file:
            data = json.load(json_data_file)
            data[key]['database'] = 'bad_db'
    with open(jfile,'w') as outfile:
        json.dump(data,outfile)
    def fin():  
        os.remove(jfile)
    request.addfinalizer(fin)
    return jfile
@pytest.fixture(scope='function',params=[
                                       ("../bad_key.json","../mysql.json",'sqldb')
                                       ])
def create_bad_key_json_file(request):
    jfile,info_file,key = request.param
    with open(info_file) as json_data_file:
            data = json.load(json_data_file)
            data['bad_key'] = data.pop(key)
    with open(jfile,'w') as outfile:
        json.dump(data,outfile)
    def fin():  
        os.remove(jfile)
    request.addfinalizer(fin)
    return jfile
@pytest.fixture(scope='function',params=[
                                       ("../bad_host.json",{'sqldb':{'db':'*','host':'badhost','passwd':'*','user':'*'}})
                                       ])
def create_bad_host_json_file(request):
    jfile,key = request.param
    with open(jfile,'w') as outfile:
        json.dump(key,outfile)
    def fin():  
        os.remove(jfile)
    request.addfinalizer(fin)
    return jfile

"""Class Initialization Testing Starts Here"""
def test_missing_json():
    jfile,key = 'fake_filename','sqldb'
    with pytest.raises(EnvironmentError) as exc_info:
        sql_functions(jfile,key)
    assert exc_info.value.message == 'JSON File Could Not Be Found/Opened'
    
def test_bad_host(create_bad_host_json_file):
    key = 'sqldb'
    with pytest.raises(EnvironmentError) as exc_info:
        sql_functions(create_bad_host_json_file,key)
    assert exc_info.value.message == 'Could Not Connect To Server'

def test_bad_pass(create_bad_pass_json_file):
    key = 'sqldb'
    with pytest.raises(ValueError) as exc_info:
        sql_functions(create_bad_pass_json_file,key)
    assert exc_info.value.message == "Something is wrong with your username or password"

def test_bad_db(create_bad_db_json_file):
    key = 'sqldb'
    with pytest.raises(ValueError) as exc_info:
        sql_functions(create_bad_db_json_file,key)
    assert exc_info.value.message == 'Database does not exist'
   
def test_bad_key(create_bad_key_json_file):
    key = 'sqldb'
    with pytest.raises(ValueError) as exc_info:
        sql_functions(create_bad_key_json_file,key)
    assert exc_info.value.message == 'Key Does Not exist in JSON'

"""Select Query Creation / Sending Starts Here"""
@pytest.mark.parametrize("table,column",[
                                         (1,"Col"),
                                         ({"table:table"},"Col"),
                                         (["Tbl",2],"Col"),
                                         (("Tbl",2),"Col"),
                                         ])
def test_bad_table_type(class_instance_fixture,table,column):
    with pytest.raises(TypeError) as exc_info:
        class_instance_fixture.create_select(table,column)
    assert exc_info.value.message == 'Table must be a string or list of strings'

@pytest.mark.parametrize("table,column",[
                                         ("Tbl",1),
                                         ("Tbl",{"Col":"Col"}),
                                         ("Tbl",["Col",2]),
                                         ("Tbl",("Col",2)),
                                         ])
def test_bad_column_type(class_instance_fixture,table,column):
    with pytest.raises(TypeError) as exc_info:
        class_instance_fixture.create_select(table,column)
    assert exc_info.value.message == "Column(s) must be a string or list/tuple of strings"


@pytest.mark.parametrize("table,column,expected",[
                                         ("Tbl","*","1146 (42S02)"),
                                         ("UserInfo","Col","1054 (42S22)"),
                                         ("UserInfo",("Username","Col"),"1054 (42S22):")
                                        ]) #Expected corresponds to the mysql error code in message
def test_Tbl_Clm_not_in_db_select(class_instance_fixture,table,column,expected):
    with pytest.raises(EnvironmentError) as exc_info:
        class_instance_fixture.create_select(table,column)
    assert expected in exc_info.value.message#Testing columns and table not in db cause error

@pytest.mark.parametrize("table,column,expected",[
                                                  ("UserInfo","*",["SELECT * FROM UserInfo;",[(1, 'user1', 'pass1'),(2, 'user2', 'pass2'),(3, 'user3', 'pass3')]]),
                                                  ("UserInfo","Username",["SELECT Username FROM UserInfo;",[('user1',),('user2',),('user3',)]]),
                                                  ("UserInfo",("Username","Password"),["SELECT Username , Password FROM UserInfo;",[('user1', 'pass1'),('user2', 'pass2'),('user3', 'pass3')]]),
                                                  (("TestCases","Results"),["TestCases.TCID","Results.PassFail"],["SELECT TestCases.TCID , Results.PassFail FROM TestCases INNER JOIN Results;",[(1, 0),(2, 0),(3, 0),(1, 1),(2, 1),(3, 1),(1, 0),(2, 0),(3, 0)]]) #AVOID DOING INNER JOINS WITHOUT WHERE CLAUSE
                                                  ])
def test_correct_select_output_no_wheres(class_instance_fixture,table,column,expected):
    temp = class_instance_fixture.create_select(table,column)
    assert expected[0] == temp[0] and expected[1] == temp[1]

@pytest.mark.parametrize("table,column,where,expected",[
                                                        ("Results","*",{"PassFail":1},["SELECT * FROM Results WHERE PassFail = '1';",[(1, None)]]),
                                                        ("Results","FailReason",{"PassFail":0},["SELECT FailReason FROM Results WHERE PassFail = '0';",[('Network',),('Unknown',)]]),
                                                        (["UserInfo","TestCases"],"*",{"UserInfo.UserID":"TestCases.TCID"},["SELECT * FROM UserInfo INNER JOIN TestCases ON UserInfo.UserID = TestCases.TCID;",[(1, 'user1', 'pass1', 1, datetime.datetime(2012,12,12,0,0)),(2, 'user2', 'pass2', 2, datetime.datetime(2013,12,12,0,0)),(3, 'user3', 'pass3', 3, datetime.datetime(2014,12,12,0,0))]]),
                                                        ("Results",["PassFail","FailReason"],{"FailReason":"IS NULL"},["SELECT PassFail , FailReason FROM Results WHERE FailReason IS NULL;",[(1, None)]])
                                                        ])
def test_correct_select_with_single_where(class_instance_fixture,table,column,where,expected):
    temp = class_instance_fixture.create_select(table,column,**where)
    assert expected[0]== temp[0] and expected[1] == temp[1]

@pytest.mark.parametrize("table,column,where,expected",[
                                                        ("Results","*",{"PassFail":"0","FailReason":"IS NOT NULL"},[(0, 'Network'),(0, 'Unknown')]),
                                                        (["UserInfo","TestCases"],"*",{"UserInfo.UserID":"TestCases.TCID","UserInfo.Username":"IS NOT NULL"},[(1, 'user1', 'pass1', 1, datetime.datetime(2012,12,12,0,0)),(2, 'user2', 'pass2', 2, datetime.datetime(2013,12,12,0,0)),(3, 'user3', 'pass3', 3, datetime.datetime(2014,12,12,0,0))])
                                                        ])
def test_correct_select_with_multiwhere(class_instance_fixture,table,column,where,expected):
    temp = class_instance_fixture.create_select(table,column,**where)
    assert expected == temp[1]
    #Can't check the query matches because the order from where clause dictionary is unpredictable

"""Insert/Update Creation/Sending Starts Here"""

@pytest.mark.parametrize("update,table,values",[
                                                (True,2,["val","val"]),
                                                (False,{"Tbl":"Tbl"},["Val","Val"]),
                                                (True,["tbl","tbl"],("val","val")),
                                                (False,("tbl","tbl"),["val","val"])
                                                ])
def test_bad_table_types(class_instance_fixture,update,table,values):
    with pytest.raises(ValueError) as exc_info:
        class_instance_fixture.upsert(update,table,values)
    if isinstance(table,(list,tuple)):
        assert exc_info.value.message == 'Insert Only Accepts One Table Name'
    else:
        assert exc_info.value.message == 'Table Name Must Be String'
        
@pytest.mark.parametrize("update,table,values",[
                                                (True,"TBL",[]),
                                                (False,"tbl",()),
                                                (True,"tbl",2),
                                                (False,"tbl",{"val1":"val"})
                                                ])
def test_bad_values_types(class_instance_fixture,update,table,values):
    with pytest.raises(ValueError) as exc_info:
        class_instance_fixture.upsert(update,table,values)
    if isinstance(values,(list,tuple)) and len(values) == 0:
        assert exc_info.value.message == 'Values Cannot Be Empty'
    else:
        assert exc_info.value.message == 'Insert Requires Values in a list,tuple,or string'

@pytest.mark.parametrize("update,table,value,expected",[
                                         (True,"Tbl",['val'],"1146 (42S02)"),
                                         (False,"TestCases","val","1136 (21S01)"),
                                         (True,"TestCases",("val","val","val"),"1136 (21S01)")
                                        ]) #Expected corresponds to the mysql error code in message
def test_upsert_sql_errors(class_instance_fixture,update,table,value,expected):
    with pytest.raises(EnvironmentError) as exc_info:
        class_instance_fixture.upsert(update,table,value)
    assert expected in exc_info.value.message#Testing columns and table not in db cause error

@pytest.mark.parametrize("update,table,value,columns,expected,select,delete",[
                                                                (True,"UserInfo",[1,"user10","pass10"],[],["REPLACE INTO UserInfo VALUES ('1','user10','pass10');",[(1, 'user10', 'pass10')]],"SELECT * FROM UserInfo WHERE UserID = 1 AND Username = 'user10' AND Password = 'pass10';","REPLACE INTO UserInfo VALUES ('1','user1','pass1');"),
                                                                (False,"Results",[(2,"Fail"),(3,"NULL")],[],["INSERT INTO Results VALUES ('2','Fail'),('3',NULL);",[(2, 'Fail'),(3, None)]],"SELECT * FROM Results WHERE PassFail > 1;", "DELETE FROM Results WHERE PassFail > 1;"),
                                                                (False,"TestCases",[(4,datetime.date(2000,12,12)),(5,datetime.date(2011,12,12))],["TCID","TimeRun"],["INSERT INTO TestCases (TCID, TimeRun) VALUES ('4','2000-12-12'),('5','2011-12-12');",[(4, datetime.datetime(2000,12,12)),(5, datetime.datetime(2011,12,12))]],"SELECT * FROM TestCases WHERE TCID > 3;","DELETE FROM TestCases WHERE TCID > 3;"),
                                                                (False,"Results",('2'),["PassFail"],["INSERT INTO Results (PassFail) VALUES ('2');",[(2, None)]],"SELECT * FROM Results WHERE PassFail = 2;","DELETE FROM Results WHERE PassFail = 2;"),
                                                                (False,"Results",[0,'NULL'],[],["INSERT INTO Results VALUES ('0',NULL);",[(0, None)]],"SELECT * FROM Results WHERE PassFail = 0 AND FailReason IS NULL;","DELETE FROM Results WHERE PassFail = 0 AND FailReason IS NULL;"),
                                                                (False,"TestCases",[(4,"NULL"),(5,"NULL")],[],["INSERT INTO TestCases VALUES ('4',NULL),('5',NULL);",[(4, None),(5, None)]],"SELECT * FROM TestCases WHERE TCID > 3;","DELETE FROM TestCases WHERE TCID > 3;")
                                                                ])
def test_correct_upserts(class_instance_fixture,reset_schema,update,table,value,columns,expected,select,delete):
    if columns:
        temp = class_instance_fixture.upsert(update,table,value,*columns)
    else:
        temp = class_instance_fixture.upsert(update,table,value)
    result = class_instance_fixture.send_query(select)
    #class_instance_fixture.send_query(delete)
    assert expected[0] == temp[0] and result[1] == expected[1]

'''Test delete_rows'''

@pytest.mark.parametrize("table,wheres,expected",[
                                                  (2,{"Clm":"val"},"Table Name Must Be String"),
                                                  ({"Tbl":"Tbl"},{"Clm":"val"},"Table Name Must Be String"),
                                                  (["tbl","tbl"],{"Clm":"val"},"Delete Only Accepts One Table Name"),
                                                  (("tbl","tbl"),{"Clm":"val"},"Delete Only Accepts One Table Name"),
                                                  ('Results',["clm","val"],"Where Clauses Must be a Non-Empty Dictionary"),
                                                  ('Results',{},"Where Clauses Must be a Non-Empty Dictionary")
                                                                ])
def test_bad_arg_types(class_instance_fixture,table,wheres,expected):
    with pytest.raises(ValueError) as exc_info:
        class_instance_fixture.delete_rows(table,wheres)
    assert exc_info.value.message == expected
    
@pytest.mark.parametrize("table,wheres,expected,select,insert",[
                                                  ("Results",{"PassFail":"IS NULL"},"DELETE FROM Results WHERE PassFail IS NULL;","SELECT * FROM Results WHERE PassFail IS NULL;","INSERT INTO Results VALUES (1,NULL);"),
                                                  (["Results"],{"PassFail":"IS NULL"},"DELETE FROM Results WHERE PassFail IS NULL;","SELECT * FROM Results WHERE PassFail IS NULL;","INSERT INTO Results VALUES (1,NULL);"),
                                                  (("Results"),{"PassFail":"IS NULL"},"DELETE FROM Results WHERE PassFail IS NULL;","SELECT * FROM Results WHERE PassFail IS NULL;","INSERT INTO Results VALUES (1,NULL);")
                                                  ])
def test_correct_deletes_single_where(class_instance_fixture,reset_schema,table,wheres,expected,select,insert):
    temp = class_instance_fixture.delete_rows(table,wheres)
    check = class_instance_fixture.send_query(select)
    #class_instance_fixture.send_query(insert)
    assert expected == temp[0] and check[1] == []
    
@pytest.mark.parametrize("table,wheres,expected,select,insert",[
                                                  ("UserInfo",{"UserID":"1","Username":'IS NOT NULL'},["DELETE FROM UserInfo","UserID = '1'","Username IS NOT NULL"],"SELECT * FROM UserInfo WHERE UserID = 1 AND Username IS NOT NULL;","INSERT INTO UserInfo VALUES (1,'user1','pass1');"),
                                                  (["UserInfo"],{"UserID":"2","Username":'IS NOT NULL'},["DELETE FROM UserInfo","UserID = '2'","Username IS NOT NULL"],"SELECT * FROM UserInfo WHERE UserID = 2 AND Username IS NOT NULL;","INSERT INTO UserInfo VALUES (2,'user2','pass2');"),
                                                  (("UserInfo"),{"UserID":"3","Username":'IS NOT NULL'},["DELETE FROM UserInfo","UserID = '3'","Username IS NOT NULL"],"SELECT * FROM UserInfo WHERE UserID = 3 AND Username IS NOT NULL;","INSERT INTO UserInfo VALUES (3,'user3','pass3');")
                                                  ])
def test_correct_deletes_muli_wheres(class_instance_fixture,reset_schema,table,wheres,expected,select,insert):
    temp = class_instance_fixture.delete_rows(table,wheres)
    check = class_instance_fixture.send_query(select)
    #class_instance_fixture.send_query(insert)
    for i in expected:
        assert i in temp[0] and check[1] == []
