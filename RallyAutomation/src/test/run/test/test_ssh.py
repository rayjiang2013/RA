'''
Created on Feb 9, 2015

@author: ljiang
'''
import pytest
import sys
import os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from test_fixture_base import test_config_module
from ssh import ssh
import inspect
from copy import deepcopy
import json

class TestSSH:
    
    @pytest.fixture(scope="class",params=[{'ip':'10.61.46.70','port':22,'username':'thot','password':'thot123'}])#,{'ip':'127.0.0.1','port':22,'username':'ljiang','password':'Jag6413682'},{'ip':'10.10.2.59','port':22,'username':'lei','password':'spirent'}])
    def config_class(self,request,test_config_module):
        print ("setup_class    class:%s" % self.__class__.__name__)
        parent_path=os.path.dirname(os.path.dirname(__file__))
        # Read ssh configuration parameters from the ssh.json
        with open(parent_path+'/ssh.json') as data_file:    
            data = json.load(data_file)
        
        #rally=test_config_module[0]
        data_to_ssh=deepcopy(data)
        data_to_ssh['ssh']=request.param
        ssh_obj=ssh(data_to_ssh)
        connection=ssh_obj.setupConnection()
        
        def fin():
            print ("teardown_class class:%s" % self.__class__.__name__)
            ssh_obj.tearConnection(connection)
                
        request.addfinalizer(fin)
        
        return connection,ssh_obj        
            
            
    @pytest.fixture(scope="function",params=['lei','12345','lei123'])
    def config_test_remote_mkdir(self,request,config_class):
        print ("setup_method    method:%s" % inspect.stack()[0][3])
        connection,ssh_obj=config_class        
        def fin():
            print ("teardown_method method:%s" % inspect.stack()[0][3])
            connection.exec_command('rm -r \\%s' % request.param)
        
        request.addfinalizer(fin)
        
        return request.param        
            
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

    @pytest.fixture(scope="function",params=[['lei.log','windows']])
    def config_test_read_log(self,request,config_class):
        print ("setup_method    method:%s" % inspect.stack()[0][3])
        connection,ssh_obj=config_class        
        stdin, stdout, stderr=connection.exec_command('ls')
        for line in stdout.readlines():
            if request.param[0]+'\n' == line:
                break
        else: 
            if request.param[1]=='windows':    
                stdin_3, stdout_3, stderr_3=connection.exec_command('type NUL > %s' % request.param[0])
                print stderr_3.readlines()
                stdin_3, stdout_3, stderr_3=connection.exec_command('echo this is for test\n > %s' % request.param[0])
            else:                
                stdin_1, stdout_1, stderr_1=connection.exec_command('touch %s' % request.param[0])
                print stderr_1.readlines()
                stdin_2, stdout_2, stderr_2=connection.exec_command('echo "this is for test" > %s' % request.param[0])
                print stderr_2.readlines()
        def fin():
            print ("teardown_method method:%s" % inspect.stack()[0][3])
            
            connection.exec_command('rm %s' % request.param[0])
        
        request.addfinalizer(fin)
        
        return request.param[0]
        
   
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
    
    @pytest.mark.parametrize("cmd", ['ls','pwd'])      
    def test_run_cmd(self,config_class,cmd):
        print 'test_run_cmd  <============================ actual test code'
        connection,ssh_obj=config_class
        stdin, stdout, stderr=ssh_obj.runCMD(connection,cmd)
        error_message=stderr.readlines()
        assert "error" not in error_message
        
    @pytest.mark.parametrize("cmd", ['inexist_command'])      
    def test_negative_run_cmd(self,config_class,cmd):
        print 'test_negative_run_cmd  <============================ actual test code'
        connection,ssh_obj=config_class
        stdin, stdout, stderr=ssh_obj.runCMD(connection,cmd)
        error_message=stderr.readlines()
        assert "not found" in "".join(error_message)
