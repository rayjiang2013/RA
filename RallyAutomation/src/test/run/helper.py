'''
To provide supporting functions to fulfill tasks like search, replace and etc.

@author: ljiang
'''
from copy import deepcopy
import re
import constants
import inspect
import sys
from pyral.restapi import Rally

class helper(object):
    '''
    To provide supporting functions to fulfill tasks like search, replace and etc.
    @summary: This class is to provide supporting functions to fulfill tasks like search, replace and etc.
    @status: under development
    @ivar data: dictionary parsed from extra.json
    @ivar rally: Rally session object
    '''
    def __init__(self,rally,data):
        self.rally=rally
        self.data=data

    #Replace all fields under a step (setup/execution/...) all at once
    def repAll(self,indexes,lst,parrent_tc,variable_value_dict,tc,steps_type,search_path,setup_calls,search_index,verdict):
        '''
        @summary: Replace all fields under a step (setup/execution/...) all at once
        @status: completed
        @type indexes: list
        @param indexes: list of indexes, for example INDEXES_SUP - referring to constants.py
        @type lst: list
        @param lst: list of test case related data
            parsed from Rally QA_TC_PARAMS_TEXT field in each Test Case
        @param parrent_tc: object of parent TestCase that calls this test case
        @param tc: object of class TestCase with Rally TestCase data
        @type variable_value_dict: dictionary
        @param variable_value_dict: dictionary of all saved variables/parameters for
            api level test cases or functional level test cases run within this test case
        @type verdict: list
        @param verdict: pass or fail verdicts for all test cases under the test set
        @type search_path: unicode
        @param search_path: path to search through the variable_value_dict
        @type steps_type: integer
        @param steps_type: test case execution steps. Please refer to definition in constants.py
        @type setup_calls: list
        @param setup_calls: list of setup api or functional level calls
        @type search_index: integer
        @param search_index: provide index to determine which value to replace
            if it finds more than one fields during the search of variable dictionary.
        @return: return rep_status: return True if replace successfully else return False,
            lst, varbs: list of variables,
            missing_varbs: list of variables that are not defined in extra.json or pre-defined local variables,
            missing_varbs_string: concatenated string of missing varbs 
        '''
        missing_varbs_string=""
        rep_status=True
        missing_varbs=[]
        varbs=[]
        for idx in indexes:
            if '$' in lst[idx]:
                if parrent_tc!=None:
                    rep_status,lst[idx],varbs,missing_varbs=self.rep(lst[idx],variable_value_dict,tc.Name,parrent_tc.Name,steps_type,search_path,setup_calls,search_index)
                if parrent_tc==None:
                    rep_status,lst[idx],varbs,missing_varbs=self.rep(lst[idx],variable_value_dict,tc.Name,"",steps_type,search_path,setup_calls,search_index)
                if rep_status==False:
                    missing_varbs_string=missing_varbs[0]
                    for i in missing_varbs:
                        if len(missing_varbs)==1:                                    
                            break
                        if missing_varbs.index(i)>0:
                            missing_varbs_string=missing_varbs_string+", "+i
        return rep_status,lst,varbs,missing_varbs,missing_varbs_string

    #Replace one JSON Request
    def repOneJSONRequest(self,api_json_request,variable_value_dict,tc,parrent_tc,steps_type,search_path,setup_calls,search_index):
        '''
        @summary: Replace one http request content from variable to actual values
        @status: completed
        @type api_json_request: unicode
        @param api_json_request: string of http request content
        @param parrent_tc: object of parent TestCase that calls this test case
        @param tc: object of class TestCase with Rally TestCase data
        @type variable_value_dict: dictionary
        @param variable_value_dict: dictionary of all saved variables/parameters for
            api level test cases or functional level test cases run within this test case
        @type search_path: unicode
        @param search_path: path to search through the variable_value_dict
        @type steps_type: integer
        @param steps_type: test case execution steps. Please refer to definition in constants.py
        @type setup_calls: list
        @param setup_calls: list of setup api or functional level calls
        @type search_index: integer
        @param search_index: provide index to determine which value to replace
            if it finds more than one fields during the search of variable dictionary.
        @return: return rep_status: return True if replace successfully else return False,
            api_json_request, varbs: list of variables,
            missing_varbs: list of variables that are not defined in extra.json or pre-defined local variables,
            missing_varbs_string: concatenated string of missing varbs 
        '''
        missing_varbs_string=""
        rep_status=True
        missing_varbs=[]
        varbs=[]
        if '$' in api_json_request:
            if parrent_tc!=None:
                rep_status,api_json_request,varbs,missing_varbs=self.rep(api_json_request,variable_value_dict,tc.Name,parrent_tc.Name,steps_type,search_path,setup_calls,search_index)
            if parrent_tc==None:
                rep_status,api_json_request,varbs,missing_varbs=self.rep(api_json_request,variable_value_dict,tc.Name,"",steps_type,search_path,setup_calls,search_index)
            if rep_status==False:
                missing_varbs_string=missing_varbs[0]
                for i in missing_varbs:
                    if len(missing_varbs)==1:                                    
                        break
                    if missing_varbs.index(i)>0:
                        missing_varbs_string=missing_varbs_string+", "+i   
        return rep_status,api_json_request,varbs,missing_varbs,missing_varbs_string


    #Replace variable
    def rep(self,strg,variable_value_dict,api_call,parrent_tc_name,steps_type,search_path,setup_calls,search_index):
        '''
        @summary: Replace one http request content from variable to actual values
        @status: completed
        @type strg: unicode
        @param strg: string of json object
        @type api_call: unicode
        @param api_call: the name of api call
        @type parrent_tc_name: unicode
        @param parrent_tc_name: name of parent TestCase that calls this test case
        @type variable_value_dict: dictionary
        @param variable_value_dict: dictionary of all saved variables/parameters for
            api level test cases or functional level test cases run within this test case
        @type search_path: unicode
        @param search_path: path to search through the variable_value_dict
        @type steps_type: integer
        @param steps_type: test case execution steps. Please refer to definition in constants.py
        @type setup_calls: list
        @param setup_calls: list of setup api or functional level calls
        @type search_index: integer
        @param search_index: provide index to determine which value to replace
            if it finds more than one fields during the search of variable dictionary.
        @return: return verd: return True if replace successfully else return False,
            varbs: list of variables, strg: updated string of json object,
            missing_varbs: list of variables that are not defined in extra.json or pre-defined local variables
        '''
        varbs=[]
        i=0
        verd=True
        missing_varbs=[]
        search_path_list=search_path.split('/')
        search_path_list_copy=deepcopy(search_path_list)
        while True:
        #for i in xrange(0,len(strg)):
            if strg[i]=='$':
                varb=re.split('[^a-zA-Z0-9_\[\]]+',strg[i:].partition('$')[-1])[0]
                if "]]" in varb:
                    varb=varb.replace(']]',']')     
                varbs.append(varb)#partition('[\n\/\\\b\&\?\;\=\,\"]')[0])
                
                if varbs[-1] in self.data['env'].keys():
                    #for key in self.data['env'].keys():
                        #if varb==key:                            
                    strg=strg.replace('$'+varbs[-1],self.data['env'][varbs[-1]],1)
                elif varbs[-1] in self.data['accounts'].keys():
                    #for key in self.data['accounts'].keys():
                        #if varb==key:
                    strg=strg.replace('$'+varbs[-1],self.data['accounts'][varbs[-1]],1)
                elif re.match(r'\w+\[\d+\]',varb) and steps_type==constants.STEPS_SUP_EXE_FLC_VER_CLU:
                    #indx=int(re.match(r'\w+\[(\d+)\]', varb).group(1))
                    indx_list=re.findall("\[(\d+)\]", varb)
                    variable_name=re.match(r'(\w+)\[\d+\]', varb).group(1)
                    fields_found=[]
                    search_path_copy=deepcopy(search_path)
                    for i in xrange(len(indx_list)):
                        if i==0:
                            search_path_copy=search_path_copy+'/'+setup_calls[int(indx_list[0])]
                        else:
                            search_path_copy=search_path_copy+'/'+indx_list[i]
                    search_path_list_copy=search_path_copy.split('/')

                    fields_found=self.searchKeyInDicForReplace(variable_value_dict, variable_name,search_path_list_copy)
                    if len(fields_found)==0:
                        verd=False
                        missing_varbs.append(varb)   
                    if len(fields_found)>0:
                        counter=0
                        sub_indx=0
                        while counter<int(indx_list[0]):
                            if setup_calls[int(indx_list[0])]==setup_calls[counter]:
                                sub_indx+=1
                            counter+=1
                        if type(fields_found[0])==dict:
                            #fields_found[0]=sorted(fields_found[0].keys(),reverse=True)
                            strg=strg.replace('$'+varbs[-1],fields_found[0][str(sub_indx)])   
                        else: 
                            strg=strg.replace('$'+varbs[-1],fields_found[0])                         
                elif re.match(r'\w+\[\d+\]',varb) and steps_type==constants.STEPS_EXE_FLC_VER:
                    #indx=int(re.match(r'\w+\[(\d+)\]', varb).group(1))
                    variable_name=re.match(r'(\w+)\[\d+\]', varb).group(1)
                    fields_found=[]
                    
                    search_path_list_copy=deepcopy(search_path_list)
                    fields_found=self.searchKeyInDicForReplace(variable_value_dict, variable_name,search_path_list_copy)
                    if len(fields_found)==0:
                        search_path_list_copy=deepcopy(search_path_list)
                        search_path_list_copy.pop(len(search_path_list)-1)
                        fields_found=self.searchKeyInDicForReplace(variable_value_dict, variable_name,search_path_list_copy)
                        if len(fields_found)==0:
                            verd=False
                            missing_varbs.append(varb)    
                    if len(fields_found)>0:                        
                        if type(fields_found[0])==dict:
                            if search_index!=None:
                                strg=strg.replace('$'+varbs[-1],fields_found[0][str(search_index)])   
                            #fields_found[0]=sorted(fields_found[0].keys(),reverse=True)
                            else:
                                strg=strg.replace('$'+varbs[-1],fields_found[0][str(len(fields_found[0])-1)])   
                        else: 
                            strg=strg.replace('$'+varbs[-1],fields_found[0]) 
                        #strg=strg.replace('$'+varbs[-1],fields_found[0])                
                elif not re.match(r'\w+\[\d+\]',varb):
                    fields_found=[]
                    search_path_list_copy=deepcopy(search_path_list)
                    fields_found=self.searchKeyInDicForReplace(variable_value_dict, varbs[-1],search_path_list_copy)
                    if len(fields_found)==0:
                        search_path_list_copy=deepcopy(search_path_list)
                        search_path_list_copy.pop(len(search_path_list)-1)
                        fields_found=self.searchKeyInDicForReplace(variable_value_dict, varbs[-1],search_path_list_copy)
                        if len(fields_found)==0:
                            verd=False
                            missing_varbs.append(varb)    
                    if len(fields_found)>0:
                        if type(fields_found[0])==dict:
                            if search_index!=None:
                                strg=strg.replace('$'+varbs[-1],fields_found[0][str(search_index)])   
                            #fields_found[0]=sorted(fields_found[0].keys(),reverse=True)
                            else:
                                strg=strg.replace('$'+varbs[-1],fields_found[0][str(len(fields_found[0])-1)])   
                        else: 
                            strg=strg.replace('$'+varbs[-1],fields_found[0]) 
                else:
                    verd=False
                    missing_varbs.append(varb)
                    #return False,strg,varbs
            if len(strg)==i+1:    
                break            
                #return True,strg,varbs
            i+=1
        return verd,strg,varbs,missing_varbs


    def append_local_variable_dict_to_variable_value_dict(self,search_path_list,variable_value_dict,local_variable_dict,current_api_call):
        '''
        @summary: append local variable dictionary to the variable value dictionary with all saved variable and value pairs
        @status: completed
        @type search_path_list: list
        @param search_path_list: list of paths to search through the variable_value_dict,
            the first element is the first keyword, then the second...
        @type variable_value_dict: dictionary
        @param variable_value_dict: dictionary of all saved variables/parameters for
            api level test cases or functional level test cases run within this test case
        @type local_variable_dict: dictionary
        @param local_variable_dict: the variable and value pairs saved for current step, will be updated in variable_value_dict
        @type current_api_call: unicode
        @param current_api_call: the name of current api call
        @raise details: log errors
        @return: return the updated variable_value_dict
        '''
        i=0
        if len(search_path_list)==0:
            if current_api_call in variable_value_dict and type(variable_value_dict[current_api_call])==dict:
                pass
                variable_value_dict[current_api_call]=[variable_value_dict[current_api_call]]
                variable_value_dict[current_api_call].append(local_variable_dict)
                variable_value_dict[current_api_call]=self.remove_number_key_of_dict(self.list_to_dict(variable_value_dict[current_api_call])) 
            else: 
                variable_value_dict.setdefault(current_api_call,[]).append(local_variable_dict) 
                variable_value_dict[current_api_call]=self.remove_number_key_of_dict(self.list_to_dict(variable_value_dict[current_api_call])) 
        if len(search_path_list)==1 and search_path_list[0]==current_api_call:
            for key in local_variable_dict.keys():
                variable_value_dict.setdefault(current_api_call,{})[key]=local_variable_dict[key] 
            #variable_value_dict[current_api_call]=self.remove_number_key_of_dict(self.list_to_dict(variable_value_dict[current_api_call]))             
            i+=1
        while i < len(search_path_list):
            #if ky in variable_value_dict:
            temp=variable_value_dict[search_path_list[i]]
            #i+=1
            search_path_list.pop(i)
            if type(temp)==dict:
                self.append_local_variable_dict_to_variable_value_dict(search_path_list,temp,local_variable_dict,current_api_call)
            i+=1
        return variable_value_dict

    #search dictionary recursively
    def searchDict(self,dict1,dict2):
        '''
        @summary: search if dict2 is in dict1
        @status: obsoleted
        @type dict1: dictionary
        @param dict1: the dictionary to be searched in
        @type dict2: dictionary
        @param dict2: search this dictionary in dict1
        @return: return the status of searching, 1 means found, 2 means not found
        '''
        for item2 in dict2.items():
            for item1 in dict1.items():
                if item2[0]==item1[0]:
                    if (type(item2[1]) != dict):
                        if item2[1]==dict1[item1[0]]:
                            #verified=True
                            status=1
                            break         
                        else: 
                            status=2  
                            return status   
                    else:
                        return self.searchDict(item1[1],item2[1])
                        #break
            else:
                status=2
                return status                           
        return status  

    #search if d1 is in d2 (without list taken into consideration)
    def searchDict2(self,d1, d2, error_message):
        #print "Changes in " + ctx
        '''
        @summary: search if d1 is in d2 (without list taken into consideration)
        @status: completed
        @type d2: dictionary
        @param d2: the dictionary to be searched in
        @type d1: dictionary
        @param d1: search this dictionary in d2
        @return: return the error message if there is any
        '''
        for k in d1:
            if k not in d2:
                #print "%s:%s is missing from content of response" % (k,d1[k])
                error_message+= " '"+k+"' : "+str(d1[k])+" is missing from content of response."
        for k in d2:
            
            if k not in d1:
                #print k + " added in d2"
                continue
            
            if d2[k] != d1[k]:
                if type(d2[k]) != dict:
                    #print "%s:%s is different in content of response" % (k,str(d2[k]))
                    error_message+= " '"+k+"' : "+str(d2[k])+" in content of response is different from the expected." 
                else:
                    if type(d1[k]) != type(d2[k]):
                        error_message+= " '"+k+"' : "+str(d2[k])+" in content of response is different from the expected." 
                        continue
                    else:
                        if type(d2[k]) == dict:
                            error_message=self.searchDict2(d1[k], d2[k],error_message)
                            continue
        #print "Done with changes in " + ctx
        return error_message

    #to remove number key as much as possible
    def remove_number_key_of_dict(self,dt):
        '''
        @summary: to remove as much number key with value pairs from dictionary as possible unless it will be converted to a list
        @status: completed
        @type dt: dictionary
        @param dt: the dictionary to be updated
        @return: return the updated dt
        '''
        for i in sorted(dt.keys()):
            if i.isdigit():
                if type(dt[i])==dict:
                    for j in dt[i].keys():
                        if i in dt.keys():
                            if len(dt[i])==1:
                                if type(dt[i][j])!=dict:
                                    if j in dt.keys() and type(dt[j]) != list:
                                        if type(dt[j])==str or type(dt[j])==unicode:
                                            dt[j]=[dt[j],dt[i][j]]
                                            del dt[i]
                                        elif type(dt[j])==dict:
                                            #dt[j]=self.remove_number_key_of_dict(dt[j])
                                            #pass
                                            if i==j:
                                                dt[i]=dt[i][j]
                                    elif j in dt.keys() and type(dt[j]) == list:
                                        dt[j].append(dt[i][j])
                                        del dt[i]                 
                                    else:
                                        dt[j]=dt[i][j]
                                        del dt[i]
                                else:
                                    dt[j]=self.remove_number_key_of_dict(dt[i][j])
                                    del dt[i]
                            elif len(dt[i])==0:
                                del dt[i]
                            else:
                                for key in dt[i].keys():
                                    item={key:dt[i][key]}
                                    item=self.remove_number_key_of_dict(item)
                                    if key not in dt:
                                        dt[key]=item[key]
                                    
                                    elif type(dt[key]) is str or type(dt[key]) is unicode:
                                        dt[key]=[dt[key]]
                                        dt[key].append(item[key])
                                        dt[key]=self.list_to_dict(dt[key])
                                        dt[key]=self.remove_number_key_of_dict(dt[key])
                                    elif type(dt[key])==dict:
                                        dt[key][str(len(dt[key]))]=item[key]
                                del dt[i]
                    if i in dt and len(dt[i])==0:
                        del dt[i]
                    
                else:
                    continue
            elif type(dt[i])!=list and type(dt[i])!=dict:
                pass
            elif type(dt[i])==dict:
                dt[i]=self.remove_number_key_of_dict(dt[i])
        if len(dt)==1:
            for k in dt:
                if k.isdigit():
                    dt=dt[k]
        return dt

    #convert list to dictionary
    def list_to_dict(self,l):
        '''
        @summary: to convert a list to dictionary
        @status: completed
        @type l: list
        @param l: the list to be converted
        @return: return the resulted dictionary dt
        '''
        i=0
        while i<len(l):
            if type(l[i])==dict: 
                for key in l[i].keys():
                    if type(l[i][key])==list:
                        l[i][key]=self.list_to_dict(l[i][key])         
                pass
            elif type(l[i])==list:
                l[i]=self.list_to_dict(l[i])
            i+=1
        #l.sort()
        dt=dict(zip(map(str, range(len(l))),l))
        return dt

    #search if d1 is in d2 (with list taken into consideration)
    def searchDict3(self,d1, d2, error_message):
        '''
        @summary: search if d1 is in d2 (with list taken into consideration)
        @status: completed
        @type d2: dictionary
        @param d2: the dictionary to be searched in
        @type d1: dictionary
        @param d1: search this dictionary in d2
        @type error_message: string
        @param error_message: error string if there is any
        @return: return the error message if there is any
        '''
        for k in d1:
            if (k not in d2) and (not k.isdigit()):
                #print "%s:%s is missing from content of response" % (k,d1[k])
                error_message+= " '"+k+"' : "+str(d1[k])+" is missing from content of response."
                continue
            elif k.isdigit():
                if d1[k] not in d2.values():
                    if type(d1[k])==dict:
                        if type(d2)==dict:
                            #for value in d2.values():
                                #if type(value)==dict:
                            error_message=self.searchDict3(d1[k],d2, error_message)
                        #if d1[k]
                        continue
                    error_message+= " '"+str(d1[k])+"' is missing from content of response."
                    continue
            else:#(k in d2) and (not k.isdigit())
                if type(d1[k])==list: 
                    d1[k]=self.list_to_dict(d1[k])
                    d1[k]=self.remove_number_key_of_dict(d1[k])   
                    if type(d2[k])==list:
                        d2[k]=self.list_to_dict(d2[k])
                        d2[k]=self.remove_number_key_of_dict(d2[k])   
                    
                    if type(d2[k])==str or type(d2[k])==unicode:
                        if type(d1[k])==list or type(d1[k])==dict:
                            for item in d1[k].values():
                                if d2[k]!=item:
                                    error_message+=" '"+k+"' : "+str(item)+" is missing from content of response."
                                    continue                         
        key_check=[]
        for k in d2:            
            if k not in d1:
                #print k + " added in d2"
                #error_message+=" '"+k+"' : "+str(d2[k])+" in content of response is different from the expected."
                continue            
            if d2[k] != d1[k]:
                if type(d2[k])==list and type(d1[k])!=list and type(d1[k])!=dict:
                    if d1[k] in d2[k]:
                        continue                 
                    else:
                        error_message+=" '"+k+"' : "+str(d2[k])+" in content of response is different from the expected."    
                elif type(d2[k]) != dict and type(d1[k])==dict:
                    #print "%s:%s is different in content of response" % (k,str(d2[k]))
                    if type(d2[k])==list:
                        d2[k]=self.list_to_dict(d2[k]) 
                        d2[k]=self.remove_number_key_of_dict(d2[k])                       
                        error_message=self.searchDict3(d1[k],d2[k],error_message)        
                        continue                                    
                    for key in d1[k].keys():
                        if key.isdigit(): 
                            if d2[k] == d1[k][key]:
                                break
                    else:
                        error_message+= " '"+k+"' : "+str(d2[k])+" in content of response is different from the expected." 
                        continue
                elif type(d2[k])==dict and type(d1[k])!=dict:
                    
                    for kyy in d2[k].keys():
                        if not kyy.isdigit():
                            pass
                        else:
                            if d2[k][kyy]==d1[k]:
                                if len(key_check)==0 or key_check[-1] == kyy:
                                    key_check.append(kyy)
                                    break                                    
                    else: 
                        error_message+=" '"+k+"' : "+str(d2[k])+" in content of response is different from the expected." 
                        continue
                elif type(d2[k])==dict and type(d1[k])==dict:
                    error_message=self.searchDict3(d1[k], d2[k],error_message)
                    continue
                else:
                    if type(d1[k]) != type(d2[k]):
                        if d2[k] in d1[k]:
                            continue
                        else:
                            error_message+= " '"+k+"' : "+str(d2[k])+" in content of response is different from the expected." 
                            continue
                    else:
                        if type(d2[k]) == list:
                            d2[k]=self.list_to_dict(d2[k]) 
                            d2[k]=self.remove_number_key_of_dict(d2[k])
                            d1[k]=self.list_to_dict(d1[k]) 
                            d1[k]=self.remove_number_key_of_dict(d1[k])
                            error_message=self.searchDict3(d1[k], d2[k],error_message)
                            continue
                        else:
                            if d1[k]==d2[k]:
                                continue
                            elif k.isdigit():
                                if d2[k] not in d1.values():
                                    error_message+= " '"+str(d2[k])+"' in content of response is different from the expected."       
                                    continue                         
                            else:
                                error_message+= " '"+k+"' : "+str(d2[k])+" in content of response is different from the expected."
                                continue
        #print "Done with changes in " + ctx
        return error_message


    def searchKeyInDic(self,search_dict, field,search_path_list):
        """
        @summary: Takes a dict with nested lists and dicts,
            and searches all dicts for a key of the field
            provided (with search path). Return all values found
        @status: completed
        @type search_dict: dictionary
        @param search_dict: the dictionary to be searched in
        @type field: unicode
        @param field: key to be searched
        @type search_path_list: list
        @param search_path_list: list of paths to search through the search_dict,
            the first element is the first keyword, then the second...
        @return: return a list of values found
        """
        #Need continue work on this 
        fields_found = []
        #search_path_list=search_path.split("/")
        if len(search_path_list)==0:
            if field in search_dict.keys():
                fields_found.append(search_dict[field])
        else:
            #search_path_list_copy=deepcopy(search_path_list)
            for item in search_path_list:
                if type(search_dict)==dict:
                    if item in search_dict.keys():                    
                        search_path_list.remove(item)
                        fields_found=self.searchKeyInDic(search_dict[item], field,search_path_list)
                elif type(search_dict)==list:
                    if type(item)==list:
                        search_path_list.remove(item)
                        for idx in item:
                            fields_found.append(self.searchKeyInDic(search_dict[idx], field,search_path_list))
        return fields_found

    def searchKeyInDicNoSearchPath(self,search_dict, field):
        """
        @summary: Takes a dict with nested lists and dicts,
            and searches all dicts for a key of the field
            provided (without search path).
        @status: completed
        @type search_dict: dictionary
        @param search_dict: the dictionary to be searched in
        @type field: unicode
        @param field: key to be searched
        @return: return a list of values found
        """
        fields_found = []
        for key, value in search_dict.iteritems():
            if key == field:
                fields_found.append(value)         
            elif isinstance(value, dict):
                results = self.searchKeyInDicNoSearchPath(value, field)
                for result in results:
                    fields_found.append(result)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        more_results = self.searchKeyInDicNoSearchPath(item, field)
                        for another_result in more_results:
                            fields_found.append(another_result)
        return fields_found

    def searchKeyInDicForReplace(self,search_dict, field,search_path_list):
        """
        @summary: Takes a dict with nested lists and dicts,
            and searches all dicts for a key of the field
            provided (with search path). This will always return a list of one element
            for replacement. Used by rep function
        @status: completed
        @type search_dict: dictionary
        @param search_dict: the dictionary to be searched in
        @type field: unicode
        @param field: key to be searched
        @type search_path_list: list
        @param search_path_list: list of paths to search through the search_dict,
            the first element is the first keyword, then the second...
        @return: return a list of values found
        """
        fields_found = []
        #search_path_list=search_path.split("/")
        if len(search_path_list)==0:
            if field in search_dict.keys():
                fields_found.append(search_dict[field])
        elif len(search_path_list)==1 and search_path_list[-1].isdigit():
            fields_found.append(search_dict[field][int(search_path_list[-1])])
        else:
            #search_path_list_copy=deepcopy(search_path_list)
            for item in search_path_list:
                if item.isdigit():
                    #search_path_list.remove(item)
                    fields_found=self.searchKeyInDicForReplace(search_dict, field,search_path_list)
                if item in search_dict.keys():                    
                    search_path_list.remove(item)
                    fields_found=self.searchKeyInDicForReplace(search_dict[item], field,search_path_list)
        return fields_found                
    