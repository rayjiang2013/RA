'''
Created on Feb 9, 2015

@author: ljiang
'''
import paramiko
import logging
import sys
import inspect
import time
'''
ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect('127.0.0.1', username='ljiang', password='Jag6413682')
stdin, stdout, stderr = ssh.exec_command("sudo dmesg")
stdin.write('Jag6413682\n')
stdin.flush()
data = stdout.readlines()
print data
'''

class ssh():
    def __init__(self,rally,data):
        '''
        Constructor
        '''
        self.data=data
        self.rally=rally
        #setup("logging.json")
        #logger.debug("testObject is initiated successfully")
        self.logger = logging.getLogger(__name__)
        self.logger.propagate=False

    def setupConnection(self):
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
    '''
    def closeLog(self,remote_file):
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
    '''
    def runTHoT(self,connection):
        try:
            '''
            stdin, stdout, stderr=connection.exec_command("C:/THoT/THoT.bat")
            time.sleep(60)
            stdin.write("\n")
            time.sleep(1)
            stdin.write("\n")
            time.sleep(1)
            stdin.write("\n")
            time.sleep(1)
            stdin.write("\n")
            time.sleep(1)
            stdin.write("\n")
            time.sleep(1)
            stdin.write("\n")
            time.sleep(1)
            stdin.write("\n")
            time.sleep(1)
            stdin.write("\n")
            time.sleep(1)
            stdin.write("\n")
            time.sleep(1)
            stdin.write("\n")
            time.sleep(1)
            stdin.write("\n")
            time.sleep(1)
            stdin.write("\n")
            time.sleep(1)
            stdin.write("\n")
            time.sleep(1)
            stdin.write("\n")
            time.sleep(1)
            stdin.write("\n")
            time.sleep(1)
            stdin.write("\n")
            time.sleep(1)

            stdin.write("EXIT\n")
            time.sleep(2)
            stdin.write("EXIT\n")
            time.sleep(2)
            stdin.write("EXIT\n")
            time.sleep(2)
            stdin.write("EXIT\n")
            time.sleep(2)
            stdin.write("EXIT\n")
            time.sleep(2)
            '''

            '''
            stdin, stdout, stderr=connection.exec_command("cd C:/THoT/TH_Protocol/")
            print stderr.readlines()
            print stdout.readlines()
            stdin4, stdout4, stderr4=connection.exec_command("chdir")
            print stderr4.readlines()
            print stdout4.readlines()
            stdin1, stdout1, stderr1=connection.exec_command("mono TH_Protocol.exe")
            stdin2, stdout2, stderr2=connection.exec_command("cd C:/THoT/TH_Node/")
            stdin3, stdout3, stderr3=connection.exec_command("mono TH_Node.exe")         
               
            #print stderr.readlines()
            stdin1.write("EXIT\n")
            stdin1.flush()
            stdin1.write("EXIT\n")
            stdin1.flush() 
            
            stdin3.write("EXIT\n")
            stdin3.flush()
            stdin3.write("EXIT\n")
            stdin3.flush() 
            
            print stdout1.readlines()
            print stdout3.readlines()
            
            stdin.write("EXIT\n")
            #stdin.flush()
            stdin.write("EXIT\n")
            stdin.flush() 
            ''' 
            
            
            stdin, stdout, stderr=connection.exec_command("mono C:/THoT/TH_Protocol/TH_Protocol.exe")
            stdin1, stdout1, stderr1=connection.exec_command("mono c:/THoT/TH_Node/TH_Node.exe")
            stdin2, stdout2, stderr2=connection.exec_command("mono c:/THoT/TH_CLI/TH_CLI.exe")
            stdin2.write("TH_REGISTERSUITE -config C:/Perf-C100MPS3.xml\n")
            time.sleep(30)
            #stdin2.write("\n")
            #stdin2.write("TH_UNREGISTERSUITE -suite TH_Suite3\n")
            stdin2.write("TH_STARTSUITE -suite TH_Suite13\n")
            time.sleep(30)
            #stdin2.write("\n")
            #stdin.write("EXIT\n")
            #stdin.write("\x03")
            #stdin1.write("EXIT\n")
            #stdin1.write("\\x03")
            #stdin1.write("\n")
            #stdin2.write("EXIT\n")
            #stdin.flush()
            #stdin1.flush()
            stdin2.flush()
            stdin3, stdout3, stderr3=connection.exec_command("taskkill /F /IM mono.exe")

               
            
            
            '''
            stdin1, stdout1, stderr1=connection.exec_command("mono c:/THoT/TH_Node/TH_Node.exe")
            #print stderr1.readlines()
            #print stdout1.readlines()
            stdin2, stdout2, stderr2=connection.exec_command("mono c:/THoT/TH_CLI/TH_CLI.exe")
            #print stderr2.readlines()
            #print stdout2.readlines()
            stdin2.write("TH_REGISTERSUITE -config C:/Perf-C100MPS3.xml\n")
            stdin2.flush()
            stdin2.write("TH_UNREGISTERSUITE -suite TH_Suite9\n")
            #print stdout2.readlines()
            #stdin2.write("TH_STARTSUITE -suite TH_Suite4\n")
            stdin2.flush()
            
            #print stderr2.readlines()
            #print stdin2.readlines()
            #print stdout2.readlines()
            #stdin2.write("TH_STARTSUITE -suite TH_Suite23\n")
            #print stdin2.readlines()
            #print stdout2.readlines()
            #stdin3, stdout3, stderr3=connection.exec_command("TH_REGISTERSUITE -config c:\Perf-C100MPS3.xml")
            #print stderr3.readlines()
            #print stdout3.readlines()
            #stdin4, stdout4, stderr4=connection.exec_command("TH_STARTSUITE -suite TH_Suite23")
            #print stderr4.readlines()
            #print stdout4.readlines()
            '''
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
        