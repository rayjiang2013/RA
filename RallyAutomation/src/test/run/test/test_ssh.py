'''
Created on Feb 9, 2015

@author: ljiang
'''
import paramiko

from src.test.run.ssh import ssh
import pytest
import sys
from test_fixture_base import test_config_module
import inspect
from copy import deepcopy
#Test testObject/copyTS
class TestSSH:
    
    @pytest.fixture(scope="class",params=[{'ip':'10.61.46.70','port':22,'username':'thot','password':'thot123'}])#,{'ip':'127.0.0.1','port':22,'username':'ljiang','password':'Jag6413682'},{'ip':'10.10.2.59','port':22,'username':'lei','password':'spirent'}])
    def config_class(self,request,test_config_module):
        try:
            print ("setup_class    class:%s" % self.__class__.__name__)
            rally,data=test_config_module
            data_to_ssh=deepcopy(data)
            data_to_ssh['ssh']=request.param
            ssh_obj=ssh(rally,data_to_ssh)
            connection=ssh_obj.setupConnection()
            
            def fin():
                try:
                    print ("teardown_class class:%s" % self.__class__.__name__)
                    ssh_obj.tearConnection(connection)
            
                except Exception,details:
                    
                    print details
                    sys.exit(1)    
                    
            request.addfinalizer(fin)
            
            return connection,ssh_obj
        except Exception,details:
            
            print details
            sys.exit(1)            
            
            
    @pytest.fixture(scope="function",params=['lei','12345','lei123'])
    def config_test_remote_mkdir(self,request,config_class):
        try:
            print ("setup_method    method:%s" % inspect.stack()[0][3])
            connection,ssh_obj=config_class        
            def fin():
                try:
                    print ("teardown_method method:%s" % inspect.stack()[0][3])
                    connection.exec_command('rm -r \\%s' % request.param)
            
                except Exception,details:
                    
                    print details
                    sys.exit(1)    
            request.addfinalizer(fin)
            
            return request.param
        except Exception,details:
            
            print details
            sys.exit(1)            



            
    #@pytest.mark.parametrize("dirname", ['lei','12345','lei123'])        
    def test_remote_mkdir(self,config_class,config_test_remote_mkdir):
        print 'test_remote_mkdir  <============================ actual test code'
        connection,ssh_obj=config_class
        dirname=config_test_remote_mkdir
        stdin, stdout, stderr=ssh_obj.remoteMkdir(connection,dirname)
        stdin_new, stdout_new, stderr_new=connection.exec_command('ls')
        assertion=[]
        for line in stdout_new.readlines():
            if dirname+'\n' == line:
                assertion.append(True)
        assert True in assertion

    @pytest.fixture(scope="function",params=['lei.log'])
    def config_test_read_log(self,request,config_class):
        try:
            print ("setup_method    method:%s" % inspect.stack()[0][3])
            connection,ssh_obj=config_class        
            stdin, stdout, stderr=connection.exec_command('ls')
            for line in stdout.readlines():
                if request.param+'\n' == line:
                    break
            else: 
                connection.exec_command('touch %s' % request.param)
                connection.exec_command('echo "this is for test" > %s' % request.param)
            def fin():
                try:
                    print ("teardown_method method:%s" % inspect.stack()[0][3])
                    
                    connection.exec_command('rm %s' % request.param)
            
                except Exception,details:
                    
                    print details
                    sys.exit(1)    
            request.addfinalizer(fin)
            
            return request.param
        except Exception,details:
            
            print details
            sys.exit(1)            


    
    #@pytest.mark.parametrize("filename", ['123.log'])        
    def test_read_log(self,config_class,config_test_read_log):
        print 'test_read_log  <============================ actual test code'
        connection,ssh_obj=config_class
        filename=config_test_read_log
        remote_file=ssh_obj.readLog(connection,filename)
        stdin_new, stdout_new, stderr_new=connection.exec_command('cat %s' % filename)
        str=""
        for line in stdout_new.readlines():
            str+=line
        remote_file_string=remote_file.read()  
        remote_file.close() 
        assert str==remote_file_string      
        
    def test_run_THoT(self,config_class):
        print 'test_run_THoT  <============================ actual test code'
        connection,ssh_obj=config_class
        ssh_obj.runTHoT(connection)
        stdin, stdout, stderr=connection.exec_command("tasklist\n")
        processlist=stdout.readlines()
        assert "mono" not in processlist
