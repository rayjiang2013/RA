'''
To define constant variables

@author: ljiang
@summary: This module provides constant variable definitions
@status: under development
@var STEPS_SUP_EXE_FLC_VER: steps sequence of setup->execution->first level check->verification
@var STEPS_SUP_EXE_FLC_VER_CLU: steps sequence of setup->execution->first level check->verification->clean up
@var STEPS_EXE_FLC_VER: steps sequence of execution->first level check->verification
@var INDEXES_SUP: indexes associated with test case setup step obtained from custom field in Rally
@var INDEXES_EXE: indexes associated with test case execution step obtained from custom field in Rally
@var INDEXES_FLC: indexes associated with test case first level check step obtained from custom field in Rally
@var INDEXES_VER: indexes associated with test case verification step obtained from custom field in Rally
@var INDEXES_CLU: indexes associated with test case clean up step obtained from custom field in Rally
@var FAILED: status number associated with failed test case
@var SUCCESS: status number associated with successful test case
@var BLOCKED: status number associated with blocked test case
@var MAX_NOTE_LENGTH: max length of text for notes field in Rally
@var INPROGRESS: scheduled state in progress for a Rally test set
@var ACCEPTED: scheduled state accepted for a Rally test set
@var COMPLETED: scheduled state completed for a Rally test set
@var FUNC_LVL_TC: identify functional level test case
@var API_LVL_TC: identify api level test case
@var FROM_TR: generate the report from Rally test result
@var FROM_EXCEPTION: generate the report from caught exception
@var NO_TC_FIELDS: total number of fields in the test case data list
@var PING_COMMAND: a dictionary of operating system associated with the ping commands
@var CHECK_IP: ip address to check for sanity check
'''

#test case execution steps
STEPS_SUP_EXE_FLC_VER=0
STEPS_SUP_EXE_FLC_VER_CLU=1
STEPS_EXE_FLC_VER=2

#associated test step index
INDEXES_SUP=[17,18,19,20,21]
INDEXES_EXE=[0,1,2,3]
INDEXES_FLC=[4,5,6,22]
INDEXES_VER=[7,8,9,10,11]
INDEXES_CLU=[12,13,14,15,16]

#test case status
FAILED=0
SUCCESS=1
BLOCKED=2

#limitation
MAX_NOTE_LENGTH=32768

#ScheduleState in Rally
INPROGRESS=0
ACCEPTED=1
COMPLETED=2

#functional test case or api test case
FUNC_LVL_TC=0
API_LVL_TC=1

#generate the report from Rally test result or exception
FROM_TR=1
FROM_EXCEPTION=0

#number of test case fields
NO_TC_FIELDS=23

#ping commands options
PING_COMMAND = {'Darwin'  : ["ping", "-o", "-c", "2", "-t", "2"],
                'Unix'    : ["ping",       "-c", "2", "-w", "2"],
                'Linux'   : ["ping",       "-c", "2", "-w", "2"],
                'Windows' : ["ping",       "-n", "2", "-w", "2"],
                'Cygwin'  : ["ping",       "-n", "2", "-w", "2"]
                }

#IP to check
CHECK_IP = ['10.10.2.166', '10.10.3.107', '10.10.2.59',
            '10.10.3.208', 'rally1.rallydev.com', 'localhost']