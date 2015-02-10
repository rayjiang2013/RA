'''
Created on Feb 9, 2015

@author: ljiang
'''
import paramiko
import logging
import sys
import inspect
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
     
