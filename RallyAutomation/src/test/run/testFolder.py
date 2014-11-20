'''
Created on Nov 5, 2014

@author: ljiang
'''
import sys
#from pprint import pprint
#from testCase import *
import logging
#from logging import config



class testFolder:
    '''
    This is the class module for test case    
    '''
    def __init__(self, rally,data):
        '''
        Constructor
        '''
        self.data=data
        self.rally=rally
        self.logger = logging.getLogger(__name__)
        self.logger.propagate=False
    
    #Show a TestFolder identified by the FormattedID value
    def getTFByID(self):
        try:
            query_criteria = 'FormattedID = "%s"' % str(self.data['tf']['FormattedID'])
            response = self.rally.get('TestFolder', fetch=True, query=query_criteria)
            dic={}
            for tf in response:
                for key in dir(tf):
                    if not key.endswith("__"):
                        dic[key]=getattr(tf,key)
                    print key,getattr(tf,key)
                break        
            #print "Test Folder obtained, ObjectID: %s  FormattedID: %s  Content: " % (tf.oid,tf.FormattedID)
            #pprint(dic)
            self.logger.debug("Test Folder obtained, ObjectID: %s  FormattedID: %s  Content: %s" % (tf.oid,tf.FormattedID,dic))
            return tf
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            self.logger.error('ERROR: %s \n' % details, exc_info=True)
            sys.exit(1)
         
    
    #Create test case
    def createTF(self):
        tf_data = {key: value for key, value in self.data['tf'].items() if key is not 'FormattedID'} #Create a test case with all fields of data['tc'] except the key value pair of 'FormattedID'
        try:
            tf = self.rally.put('TestFolder', tf_data)
            self.logger.debug("Test folder created, ObjectID: %s  FormattedID: %s" % (tf.oid, tf.FormattedID))
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            self.logger.error('ERROR: %s \n' % details, exc_info=True)
            sys.exit(1)
        #print "Test folder created, ObjectID: %s  FormattedID: %s" % (tf.oid, tf.FormattedID)      
        return tf  
        
    #Update test case
    def updateTF(self):
        tf_data = self.data['tf']
        try: 
            tf = self.rally.post('TestFolder', tf_data)    
            self.logger.debug("Test Folder %s updated" % tf.FormattedID)      
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            self.logger.error('ERROR: %s \n' % details, exc_info=True)
            sys.exit(1)
        #print "Test Folder %s updated" % tf.FormattedID
        return tf
    
    #Delete test case
    def delTF(self):
        try: 
            delete_success=self.rally.delete('TestFolder', self.data['tf']['FormattedID'])
            if delete_success == True:
                #print "Test Folder deleted, FormattedID: %s" % self.data['tf']['FormattedID']
                self.logger.debug("Test Folder deleted, FormattedID: %s" % self.data['tf']['FormattedID'])
        except Exception, details:
            #sys.stderr.write('ERROR: %s %s %s does not exist\n' % (Exception,details,self.data['tf']['FormattedID']))
            self.logger.error('ERROR: %s %s %s does not exist\n' % (Exception,details,self.data['tf']['FormattedID']), exc_info=True)
            sys.exit(1)
        
            
    #Add test cases to test folder; remember to use _ref (ref is like abc/12345 and will result in some issue in debug mode
    #. _ref is like http://xyc/abc/12345) as reference to an object when needed. 
    #Ex: http://stackoverflow.com/questions/21718491/how-to-add-new-testcases-to-an-existing-rally-folder
    def addTC(self):
        try: 
            tf_obj=testFolder(self.rally,self.data)
            tf=tf_obj.getTFByID()
            self.data['tc']['TestFolder']=str(tf._ref)
            tc_new = self.rally.post('TestCase', self.data['tc'])   
            self.logger.debug("Test cases %s is added to Test folder %s" % (tc_new.FormattedID,tf.FormattedID))  
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            self.logger.error('ERROR: %s \n' % details, exc_info=True)
            sys.exit(1)
        #print "Test cases %s is added to Test folder %s" % (tc_new.FormattedID,tf.FormattedID)
