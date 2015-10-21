'''
To provide ssh related functionalities

@author: ljiang
'''
import paramiko
import logging
import sys
import inspect
import time
import os

class ssh(object):
    '''
    To provide ssh related functionalities
    @summary: This class is used to provide ssh related functionalities
    @status: under development
    @ivar data: dictionary parsed from extra.json
    @ivar logger: the logger for testObject
    '''
    def __init__(self,data):
        self.data=data
        #self.rally=rally
        #setup("logging.json")
        #logger.debug("testObject is initiated successfully")
        self.logger = logging.getLogger(__name__)
        self.logger.propagate=False

    def setupConnection(self):
        '''
        @summary: To setup connection with the ssh server
        @status: completed
        @raise details: log errors
        @return: return ssh session object
        '''
        try:
            ssh=paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.data['ssh']['ip'], port=self.data['ssh']['port'],username=self.data['ssh']['username'], password=self.data['ssh']['password'])       
        except Exception,details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
        self.logger.info("ssh connection with ip: %s is successfully setup" % self.data['ssh']['ip'])            
        return ssh 
        
    def tearConnection(self,connection):
        '''
        @summary: To close connection with the ssh server
        @status: completed
        @param connection: the ssh connection object
        @raise details: log errors
        @return: return ssh session object
        '''
        try:
            ssh=connection.close()
        except Exception,details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
        self.logger.info("ssh connection with ip: %s is successfully teardown" % self.data['ssh']['ip'])            
        return ssh         
    
    def remoteMkdir(self,connection,dirname):
        '''
        @summary: To create a directory in the remote server
        @status: completed
        @param connection: the ssh connection object
        @type dirname: string
        @param dirname: the name of directory
        @raise details: log errors
        @return: return stdin: standard input handler, stdout: the standard output handler, stderr: the standard error handler 
        '''
        try:
            stdin, stdout, stderr=connection.exec_command("mkdir %s" % dirname)
        except Exception,details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
        self.logger.info("A directory %s is created remotely" % dirname)            
        return stdin, stdout, stderr                 
    
    def readLog(self,connection,filename):
        '''
        @summary: To open a log for read
        @status: completed
        @param connection: the ssh connection object
        @type filename: string
        @param filename: the name of log file
        @raise details: log errors
        @return: the file object
        '''
        try:
            sftp_client=connection.open_sftp()
            remote_file=sftp_client.open(filename,mode='r')
        except Exception,details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
        self.logger.info("A log file %s is read" % filename)            
        return remote_file

    def closeLog(self,remote_file):
        '''
        @summary: To close a log
        @status: completed
        @param remote_file: the file object
        @raise details: log errors
        @return: None
        '''
        try:
            remote_file.close()
        except Exception,details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
        self.logger.info("A log file %s is closed" % remote_file.FILE)            
        return 

    def runTHoT(self,connection):
        '''
        @summary: To run the THoT test framework on remote server
        @status: completed
        @param connection: the ssh connection object
        @raise details: log errors and kill the THoT task
        @return: None
        '''
        try:
            stdin, stdout, stderr=connection.exec_command("mono C:/THoT/TH_Protocol/TH_Protocol.exe")
            stdin1, stdout1, stderr1=connection.exec_command("mono c:/THoT/TH_Node/TH_Node.exe")
            stdin2, stdout2, stderr2=connection.exec_command("mono c:/THoT/TH_CLI/TH_CLI.exe")
            stdin2.write("TH_REGISTERSUITE -config C:/Perf-C100MPS3.xml\n")
            time.sleep(30)
            stdin5, stdout5, stderr5=connection.exec_command("ls -t -d C:/THoT/TH_Suite*")
            first_line=stdout5.readline()
            suite_id=first_line.split('/')[2]
            error=stderr5.readlines()
            stdin2.write("TH_STARTSUITE -suite %s" % suite_id)
            time.sleep(30)
            stdin2.write("TH_CANCELSUITE -suite %s" % suite_id)
            time.sleep(60)
            #stdin2.write("TH_UNREGISTERSUITE -suite %s" % suite_id)
            stdin2.flush()
            stdin3, stdout3, stderr3=connection.exec_command("taskkill /F /IM mono.exe")

        except Exception,details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                stdin4, stdout4, stderr4=connection.exec_command("taskkill /F /IM mono.exe")
                raise
            else:
                #print Exception,details
                stdin4, stdout4, stderr4=connection.exec_command("taskkill /F /IM mono.exe")
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
        self.logger.info("THoT is started")            
        return 
    
    #run a generic command
    def runCMD(self,connection,cmd):
        '''
        @summary: To run a generic command through ssh
        @status: completed
        @param connection: the ssh connection object
        @type cmd: string
        @param cmd: the content of the command
        @raise details: log errors
        @return: return stdin: standard input handler, stdout: the standard output handler, stderr: the standard error handler
        '''
        try:
            stdin, stdout, stderr=connection.exec_command(cmd)
        except Exception,details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
        self.logger.info("A command %s is created remotely" % cmd)            
        return stdin, stdout, stderr   
        