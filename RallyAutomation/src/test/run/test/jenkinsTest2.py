'''
Created on Mar 11, 2015

@author: ljiang
'''
import jenkins
# Connect to instance - username and password are optional
j = jenkins.Jenkins('http://10.10.2.59:8080', 'lei', 'spirent')

# Create a new job
if not j.job_exists('empty'):
    j.create_job('empty', jenkins.EMPTY_CONFIG_XML)
j.disable_job('empty')

# Copy a job
if j.job_exists('empty_copy'):
    j.delete_job('empty_copy')
j.copy_job('empty', 'empty_copy')
j.enable_job('empty_copy')

# Reconfigure an existing job and build it
j.reconfig_job('empty_copy', jenkins.RECONFIG_XML)
j.build_job('empty_copy')

# Create a slave node
if j.node_exists('test-node'):
    j.delete_node('test-node')
j.create_node('test-node')