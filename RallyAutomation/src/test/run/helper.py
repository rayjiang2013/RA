'''
Created on Jun 9, 2015

@author: ljiang
'''
from copy import deepcopy
import re
import constants
import inspect
import sys
from pyral.restapi import Rally

class helper:
    def __init__(self,rally,data):
        self.rally=rally
        self.data=data
    
    #Replace variable
    def rep(self,strg,variable_value_dict,api_call,parrent_tc_name,steps_type,search_path,setup_calls,search_index):
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
                    indx=int(re.match(r'\w+\[(\d+)\]', varb).group(1))
                    variable_name=re.match(r'(\w+)\[\d+\]', varb).group(1)
                    fields_found=[]
                    search_path_copy=deepcopy(search_path)
                    
                    search_path_copy=search_path_copy+'/'+setup_calls[indx]
                    search_path_list_copy=search_path_copy.split('/')

                    fields_found=self.searchKeyInDicForReplace(variable_value_dict, variable_name,search_path_list_copy)
                    if len(fields_found)==0:
                        verd=False
                        missing_varbs.append(varb)   
                    '''
                    fields_list=self.searchKeyInDicForReplace(variable_value_dict, api_call,search_path_list_copy)
                    fields_dict=self.remove_number_key_of_dict(self.list_to_dict(fields_list))
                    if type(fields_dict)==dict and len(fields_dict)>0:
                        fields_found=self.searchKeyInDicForReplace(fields_dict, variable_name,search_path_list_copy)
                        if len(fields_found)==0:
                            verd=False
                            missing_varbs.append(varb)        
                    if type(fields_dict)==dict and len(fields_dict)==0:
                        #need implement recursively searchKeyInDic for parrent api name
                        fields_list=self.searchKeyInDicForReplace(variable_value_dict, parrent_tc_name,search_path_list_copy)
                        fields_dict=self.remove_number_key_of_dict(self.list_to_dict(fields_list))
                        if type(fields_dict)==dict and len(fields_dict)>0:
                            fields_found=self.searchKeyInDicForReplace(fields_dict, variable_name,search_path_list_copy)      
                            if len(fields_found)==0:
                                verd=False
                                missing_varbs.append(varb)     
                        if len(fields_dict)==0:
                            verd=False
                            missing_varbs.append(varb)                      
                    if type(fields_dict)==list:
                        
                        #for j in fields_dict:
                            #if type(j)==dict:
                                #fields_found=self.searchKeyInDic(j, varbs[-1])
                        
                        raise Exception("Should covert the list to dict first")
                    '''
                    if len(fields_found)>0:
                        counter=0
                        sub_indx=0
                        while counter<indx:
                            if setup_calls[indx]==setup_calls[counter]:
                                sub_indx+=1
                            counter+=1
                        if type(fields_found[0])==dict:
                            #fields_found[0]=sorted(fields_found[0].keys(),reverse=True)
                            strg=strg.replace('$'+varbs[-1],fields_found[0][str(sub_indx)])   
                        else: 
                            strg=strg.replace('$'+varbs[-1],fields_found[0])                         

                        #strg=strg.replace('$'+varbs[-1],fields_found[0])                     
                #elif varbs[-1] in variable_value_dict:                    
                    #strg=strg.replace('$'+varbs[-1],variable_value_dict[varbs[-1]])
                #elif True:#len(self.searchKeyInDic(variable_value_dict, api_call)) >0:
                #api_call in  variable_value_dict:             

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
                    '''
                    fields_list=self.searchKeyInDicForReplace(variable_value_dict, api_call,search_path_list_copy)
                    fields_dict=self.remove_number_key_of_dict(self.list_to_dict(fields_list))
                    if type(fields_dict)==dict and len(fields_dict)>0:
                        fields_found=self.searchKeyInDicForReplace(fields_dict, variable_name,search_path_list_copy)
                        if len(fields_found)==0:
                            verd=False
                            missing_varbs.append(varb)        
                    if type(fields_dict)==dict and len(fields_dict)==0:
                        #need implement recursively searchKeyInDic for parrent api name
                        fields_list=self.searchKeyInDicForReplace(variable_value_dict, parrent_tc_name,search_path_list_copy)
                        fields_dict=self.remove_number_key_of_dict(self.list_to_dict(fields_list))
                        if type(fields_dict)==dict and len(fields_dict)>0:
                            fields_found=self.searchKeyInDicForReplace(fields_dict, variable_name,search_path_list_copy)      
                            if len(fields_found)==0:
                                verd=False
                                missing_varbs.append(varb)     
                        if len(fields_dict)==0:
                            verd=False
                            missing_varbs.append(varb)                      
                    if type(fields_dict)==list:
                        
                        #for j in fields_dict:
                            #if type(j)==dict:
                                #fields_found=self.searchKeyInDic(j, varbs[-1])
                        
                        raise Exception("Should covert the list to dict first")
                    '''
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
                    '''
                    fields_list=self.searchKeyInDicForReplace(variable_value_dict, api_call,search_path_list)
                    fields_dict=self.remove_number_key_of_dict(self.list_to_dict(fields_list))
                        
                    if type(fields_dict)==dict and len(fields_dict)>0:
                        fields_found=self.searchKeyInDicForReplace(fields_dict, varbs[-1],search_path_list)
                        if len(fields_found)==0:
                            verd=False
                            missing_varbs.append(varb)     
     
                    if type(fields_dict)==dict and len(fields_dict)==0:
                        #need implement recursively searchKeyInDic for parrent api name
                        fields_list=self.searchKeyInDicForReplace(variable_value_dict, parrent_tc_name,search_path_list)
                        fields_dict=self.remove_number_key_of_dict(self.list_to_dict(fields_list))
                        if type(fields_dict)==dict and len(fields_dict)>0:
                            fields_found=self.searchKeyInDicForReplace(fields_dict, varbs[-1],search_path_list)    
                            if len(fields_found)==0:
                                verd=False
                                missing_varbs.append(varb)    
                        if len(fields_dict)==0:
                            verd=False
                            missing_varbs.append(varb)                                              
                    if type(fields_dict)==list:
                        
                        #for j in fields_dict:
                            #if type(j)==dict:
                                #fields_found=self.searchKeyInDic(j, varbs[-1])
                        
                        raise Exception("Should covert the list to dict first")
                    '''
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
        try:
            for item2 in dict2.items():                
                for item1 in dict1.items():
                    if item2[0]==item1[0]:
                        if (type(item2[1]) != dict):
                            if item2[1]==dict1[item1[0]]:
                                #verified=True
                                status=1
                                #verdict[-1]=(verdict[-1][0],verdict[-1][1]+' Verification is successful.')
                                #verdict.append((1,'Success: status code expected and verified'))
                                #self.logger.debug("The test execution for test case %s, build %s is verified to be successful." % (tc.FormattedID,self.data["ts"]["Build"]))  
                                break         
                            else: 
                                status=2
                                #verdict[-1]=(0,'Failure: verification failed')
                                #verified=False
                                #self.logger.debug("The test execution for test case %s, build %s is verified to be failed." % (tc.FormattedID,self.data["ts"]["Build"]))   
                                return status   
                        else:
                            return self.searchDict(item1[1],item2[1])
                            #break
                else:
                    status=2
                    #verdict[-1]=(0,'Failure: verification failed')
                    #verified=False
                    #self.logger.debug("The test execution for test case %s, build %s is verified to be failed." % (tc.FormattedID,self.data["ts"]["Build"]))   
                    return status                           
            return status
        except Exception, details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)     
    
    #search if d1 is in d2 (without list taken into consideration)
    def searchDict2(self,d1, d2, error_message):
        #print "Changes in " + ctx
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
        #for x in dt.keys():
            #if x.isdigit():
                #int(x)
        for i in sorted(dt.keys()):
            if i.isdigit():
                if type(dt[i])==dict:
                    for j in dt[i].keys():
                        if i in dt.keys():
                            if len(dt[i])==1:
                                if type(dt[i][j])!=dict:
                                    if j in dt.keys() and type(dt[j]) != list:
                                        dt[j]=[dt[j],dt[i][j]]
                                        del dt[i]
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
        return dt
            
    #convert list to dictionary
    def list_to_dict(self,l):
        i=0
        while i<len(l):
            if type(l[i])==dict: 
                for key in l[i].keys():
                    if type(l[i][key])==list:
                        '''
                        j=0
                        while j<len(l[i][key]):
                            if type(l[i][key][j])!=dict and type(l[i][key][j])!=list:
                                l[i][key].pop(j)
                                l[i][key]=l[i][key][j]
                            i++    
                        else:
                        '''
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
        #print "Changes in " + ctx
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
                    
                    if type(d2[k])!=list and type(d2[k])!=dict:
                        for item in d1[k].values():
                            if d2[k]!=item:
                                error_message+=" '"+k+"' : "+str(item)+" is missing from content of response."
                                continue
                    '''
                    elif type(d2[k])==dict:
                        for x in d1[k].keys():
                            if d1[k][x] not in d2[k].values():
                                error_message+=" '"+str(d1[k][x])+"' is missing from content of response."
                                continue  
                    elif type(d2[k])==list:
                        d2[k]=self.list_to_dict(d2[k])
                        for y in d1[k].keys():
                            if d1[k][y] not in d2[k].values():
                                error_message+=" '"+str(d1[k][y])+"' is missing from content of response."
                                continue                                  
                    '''                                              
                '''
                elif type(d1[k])==list and type(d2[k])==list:
                    d2[k]=self.list_to_dict(d2[k]) 
                    d1[k]=self.list_to_dict(d1[k]) 
                    error_message=self.searchDict3(d1[k], d2[k],error_message)
                    continue                  
                '''                            
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
                    '''
                    if k.isdigit():
                        if d2[k] in d1.values():
                            continue
                        else:
                            error_message=self.searchDict3(d1[k], d2[k],error_message)
                            continue
                    else:
                    '''
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
                                '''
                                if k.isdigit():
                                    error_message+= " '"+str(d2[k])+"' in content of response is different from the expected." 
                                    continue
                                else:
                                '''
                                error_message+= " '"+k+"' : "+str(d2[k])+" in content of response is different from the expected."
                                continue
        #print "Done with changes in " + ctx
        return error_message


    def searchKeyInDic(self,search_dict, field,search_path):
        """
        Takes a dict with nested lists and dicts,
        and searches all dicts for a key of the field
        provided.
        """
        fields_found = []
        search_path_list=search_path.split("/")
        #for item in search_path_list:
        for key, value in search_dict.iteritems():
    
            if key == field:
                fields_found.append(value)
                               
            elif isinstance(value, dict):
                results = self.searchKeyInDic(value, field,search_path)
                for result in results:
                    fields_found.append(result)
    
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        more_results = self.searchKeyInDic(item, field,search_path)
                        for another_result in more_results:
                            fields_found.append(another_result)
            
        return fields_found
    

    def searchKeyInDicForReplace(self,search_dict, field,search_path_list):
        """
        Takes a dict with nested lists and dicts,
        and searches all dicts for a key of the field
        provided.
        """
        fields_found = []
        #search_path_list=search_path.split("/")
        if len(search_path_list)==0:
            if field in search_dict.keys():
                fields_found.append(search_dict[field])
        else:
            #search_path_list_copy=deepcopy(search_path_list)
            for item in search_path_list:
                if item in search_dict.keys():                    
                    search_path_list.remove(item)
                    fields_found=self.searchKeyInDicForReplace(search_dict[item], field,search_path_list)
                
        return fields_found                
        '''        
        for key, value in search_dict.iteritems():
    
            if key == field:
                fields_found.append(value)
            elif isinstance(value, dict):
                results = self.searchKeyInDic(value, field)
                for result in results:
                    fields_found.append(result)
    
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        more_results = self.searchKeyInDic(item, field)
                        for another_result in more_results:
                            fields_found.append(another_result)
        '''

    #save values in response into variables; to do!!!!!!!!
    def saveVar(self,r_ver_content,verdict,variable_value_dict,variable_list,search_path):
        #As in firstlevelcheck()
        for varb in variable_list:
            values=self.searchKeyInDic(r_ver_content, varb,search_path)
            i=0
            if len(values)==0:
                verdict[-1]=(verdict[-1][0],verdict[-1][1]+' but failed to save values in response content to varaibles as the variable: %s cannot be found in the response content' % varb)
                self.logger.debug("Failed to save values in response content to varaible %s as it cannot be found in response content" % varb)                          
            while i < len(values) and len(values)>1:
                if values[i]!=values[i+1]:
                    verdict[-1]=(verdict[-1][0],verdict[-1][1]+' but failed to save values in response content to varaibles as there are multiple different values for variable: %s' % varb)
                    self.logger.debug("Failed to save values in response content to varaible %s as there are multiple different values for it in response" % varb)  
                    break                             
                i+=1
            else:
                variable_value_dict[varb]=values[0] 
                self.logger.debug("Successfully save values in response content to variable: %s" % varb)  
                
                
            '''
            #this is just to show what it is like in executor()
            for varb in variable_list:
                values=self.searchKeyInDic(json_request, varb)
                i=0
                if len(values)==0:
                    self.logger.debug("Failed to save values in requested json object to varaible %s as it cannot be found in the requested json object" % varb)       
                    return False,lst,variable_value_dict                   
                while i < len(values) and len(values)>1:
                    if values[i]!=values[i+1]:                            
                        self.logger.debug("Failed to save values in response content to varaible %s as there are multiple different values for it in response" % varb)  
                        return False,lst,variable_value_dict                             
                    i+=1
                else:
                    variable_value_dict[varb]=values[0] 
                    self.logger.debug("Successfully save values in response content to variable: %s" % varb)  
            '''
        return verdict,variable_value_dict
    