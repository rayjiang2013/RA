'''
Created on Mar 11, 2015

@author: ljiang
'''
from jenkinsapi.jenkins import Jenkins

def get_server_instance():
    jenkins_url = 'http://10.10.2.59:8080'
    server = Jenkins(jenkins_url, username = 'lei', password = 'spirent')
    return server

"""Enable a Jenkins job"""
def enable_job():
    # Refer Example #1 for definition of function 'get_server_instance'
    server = get_server_instance()
    job_name = 'RallyTestAutomation'
    if (server.has_job(job_name)):
        job_instance = server.get_job(job_name)
        job_instance.enabled()
        print 'Name:%s,Is Job Enabled ?:%s' %(job_name,job_instance.is_enabled())

"""Get job details of each job that is running on the Jenkins instance"""
def get_job_details():
    # Refer Example #1 for definition of function 'get_server_instance'
    server = get_server_instance()
    #build=server.get_last_build()
    for j in server.get_jobs():
        job_instance = server.get_job(j[0])
        print 'Job Name:%s' %(job_instance.name)
        print 'Job Description:%s' %(job_instance.get_description())
        print 'Is Job running:%s' %(job_instance.is_running())
        print 'Is Job enabled:%s' %(job_instance.is_enabled())



if __name__ == '__main__':
    print get_server_instance().version
    enable_job()
    get_job_details()