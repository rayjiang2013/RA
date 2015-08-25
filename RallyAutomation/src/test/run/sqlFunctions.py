'''
Created on Jul 24, 2015

@author: jwerner
'''
import mysql.connector
from mysql.connector import errorcode
import json

class sql_functions:
    """This class is used to create/test a mysql connection, create queries
        and send queries."""
    def __init__(self,file_name,sql_key):
        self.db_key = None
        try:
            with open(file_name) as json_data_file:
                data = json.load(json_data_file)
                self.db_key = data.get(sql_key)
                if self.db_key == None:             #Key could not be found or was empty dict. 
                    raise ValueError("Key Does Not exist in JSON")
        except EnvironmentError:
            raise EnvironmentError("JSON File Could Not Be Found/Opened")
        try:
            #session_config={ key:value for (key,value) in self.db_key.items() if key == "passwd" or key == "autocommit" or key == 'host' or key == 'db' or key == 'user' }
            self.cnx = mysql.connector.connect(**self.db_key) #uses all values found in json key dict.
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                raise ValueError("Something is wrong with your username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                raise ValueError("Database does not exist")
            else:
                raise EnvironmentError("Could Not Connect To Server") #bad host,port or server closed

    def create_select(self,table,columns, **wheres):
        """ This function generates sql select queries with specific 
            columns and clauses created from wheres dictionary.
            Can do multiple table queries as well if tables passed as list/tuple
            and the where clauses and columns are updated to include "table.column". """
        query = list()
        if isinstance(columns,(list,tuple)):
            for checker in columns:
                if type(checker) is not str:
                    raise TypeError("Column(s) must be a string or list/tuple of strings")
            query.append("SELECT")
            query.append(",".join(" %s " %(i) for i in columns))
        elif isinstance(columns,(str)):
            query.append("SELECT %s " %columns)
        else:
            raise TypeError("Column(s) must be a string or list/tuple of strings")
        if isinstance(table,(str)):
            query.append("FROM %s" % table)
            if wheres:
                query.append(" WHERE ")
                for k, v in wheres.iteritems():
                    v = str(v)
                    if v == 'IS NOT NULL' or v == 'IS NULL':
                        query.append("%s %s" %(k,v)) 
                        query.append(" AND ")
                    else:
                        query.append("%s = '%s'" %(k,v)) 
                        query.append(" AND ")
                query = query[:-1]
                query.append(";")
                query = "".join(query)
                data = self.send_query(query)
                return(data)
            else:
                query.append(";")
                query ="".join(query)
                data = self.send_query(query)
                return(data)
        elif isinstance(table,(tuple,list)):
            for check in table:
                if type(check) is not str:
                    raise TypeError("Table must be a string or list of strings")     
            query.append("FROM " + " INNER JOIN ".join("%s" % (i) for i in table))
            if wheres:
                query.append(" ON ")
                for k,v in wheres.iteritems():
                    v = str(v)
                    temp = v.find('.')
                    if v[0:temp] in table: #Checking if 2nd where argument is of form 'table.column' 
                        query.append("%s = %s" %(k,v))
                        query.append(" AND ")
                    elif v == 'IS NOT NULL' or v == 'IS NULL':
                        query.append("%s %s" %(k,v)) 
                        query.append(" AND ")
                    else:
                        query.append("%s = '%s'" %(k,v)) 
                        query.append(" AND ")  
                query = query[:-1]
                query.append(";")
                query = "".join(query)      
                data = self.send_query(query)  
                return(data)  
            else:
                query.append(";")
                query ="".join(query)
                data = self.send_query(query)
                return(data)
        else:
            raise TypeError("Table must be a string or list of strings")
    def upsert(self,update,table,values,*columns):
        """ Inserts row values into given table with option to only insert
            into specific columns.Update option allows you to change values
            in unique/primary key rows without causing error """
        query = list()
        if type(table) is str:  #Can only insert into one table at a time
            query.append("INSERT INTO %s" % table)
        elif isinstance(table,(tuple,list)) and len(table) > 0:
            if len(table) > 1:
                raise ValueError("Insert Only Accepts One Table Name")
            else:
                query.append("INSERT INTO %s" % table[0])
        else:
            raise ValueError("Table Name Must Be String")
        if columns:
            query.append(" (")
            query.append(", ".join("%s" % (i) for i in columns))
            query.append(")")
        query.append(" VALUES ")
        if isinstance(values,(list,tuple)):
            if len(values) == 0:
                raise ValueError("Values Cannot Be Empty")
            if isinstance(values[0],(list,tuple)): #if one element is a list/tuple, all should be
                for i in values:
                    query.append('(')
                    for x in i:
                        if x == 'NULL':
                            query.append(("%s")%x)
                            query.append(",")
                        else:
                            temp = str(x)
                            query.append(("'%s'")%temp)
                            query.append(",")
                    query = query[:-1]
                    query.append(')')
                    query.append(",")
            else:                       #this means there is only values for one row in list/tuple
                query.append('(')
                for i in values:
                    if i == 'NULL':
                            query.append(("%s")%i)
                            query.append(",")
                    else:
                        temp = str(i)
                        query.append(("'%s'")%temp)
                        query.append(",")
                query = query[:-1]
                query.append(')')
                query.append(",")
            query = query[:-1]
        elif isinstance(values,str):  #this means you are only inserting or updating one value
            if values == 'NULL':
                query.append("(%s)" %str(values))
            else:
                query.append("('%s')" %str(values))
        else:
            raise ValueError("Insert Requires Values in a list,tuple,or string")
        if update is True:
            if isinstance(table,str):
                query[0] = "REPLACE INTO %s" %table #replace into is the same as "ON DUPLICATE KEY UPDATE"
            else:
                query[0] = "REPLACE INTO %s" %table[0]
        #else:   #Un-Comment If you want to still insert rows that don't cause error on duplicate primary key
            #if isinstance(table,str):
            #    query[0] = "Insert IGNORE INTO %s" %table
            #else:
            #    query[0] = "INSERT IGNORE INTO %s" %table[0]
        query.append(";")
        query = "".join(query)
        data = self.send_query(query) 
        return(data)

    def delete_rows(self,table,wheres):
        query = ["DELETE FROM"]
        if type(table) is str:  #Can only insert into one table at a time
            query.append(" %s " % table)
        elif isinstance(table,(tuple,list)):
            if len(table) > 1:
                raise ValueError("Delete Only Accepts One Table Name")
            else:
                query.append(" %s " % table[0])
        else:
            raise ValueError("Table Name Must Be String")
        query.append("WHERE ")
        if not isinstance(wheres,dict) or len(wheres) == 0:
            raise ValueError("Where Clauses Must be a Non-Empty Dictionary")
        for k, v in wheres.iteritems():
            v = str(v)
            if v == 'IS NOT NULL' or v == 'IS NULL':
                query.append("%s %s" %(k,v)) 
                query.append(" AND ")
            else:
                query.append("%s = '%s'" %(k,v)) 
                query.append(" AND ")
        query = query[:-1]
        query.append(";")
        query = "".join(query)
        data = self.send_query(query)
        return(data)

    def send_query(self,query): 
        """Sends Query and Raises Error on Failure"""
        try:
            self.cursor = self.cnx.cursor()
            self.cursor.execute(query)
            count = 0
            select_return = [] #Can access the select query results from here
            if "SELECT" in query:
                #field_names = [i[0] for i in self.cursor.description]
                for row in self.cursor:
                    select_return.append(row) 
                    count += 1
        except mysql.connector.Error as err:
            raise EnvironmentError(str(err) + " for Query: " + query)
        else:
            results = [query,select_return,count]
            self.cursor.close()
            return (results)
    def end_connection(self):
        self.cnx.close()
