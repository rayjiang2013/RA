'''
Created on Feb 3, 2015

@author: ljiang
'''
import requests
import pycurl
import json

#s=requests.session()
#login_data={'formPosted':'1', 'login_email':'me@mainFuncs.com, 'password':'pw'}
#s.post('http://10.40.60.170/login)', login_data)
#logged in! cookies saved for future requests.
#r2 = s.get('https://localhost/profile_data.json', ...)
#cookies sent automatically!
#do whatever, s will keep your cookies intact :)

#curl -u "pv&#40;spirent.com&user:spirent&user" "http://10.40.60.170/login&nbsp;HTTP/1.1&nbsp;(application/x-www-form-urlencoded;charset=UTF-8)"
'''
s = requests.Session()
s.auth = ('pv@spirent.com', 'spirent')
response = s.get('http://10.40.60.170/login&nbsp;HTTP/1.1&nbsp;(application/x-www-form-urlencoded;charset=UTF-8)')
pass
'''

url = "http://10.10.2.166/"
ChassisIP="10.10.3.240"
s = requests.session()
#r = s.get(url,verify = False)


payload = {
"user[email]":"admin@spirent.com",
"user[password]":"spirent"
}

payload2={"user[email]":"standard@spirent.com","user[firstname]":"standard","user[lastname]":"standard","user[role]":"user","user[password]":"spirent"}

payload3='{"queue[name]":"Alpha","queue[port_groups][]":["86d185b614262931f61dc3908f1f4f74","86d185b614262931f61dc3908f1f3fc8"]}'

r = s.post(url+'login',data=payload,verify = False)
print r.content


r2=s.get(url+'av_chassis/'+ChassisIP).content

r2_dict=json.loads(r2)
print r2_dict
'''
r6=s.post(url+"av_queues/",data=json.loads(payload3),verify=False)
print r6.content

r4=s.get(url+'current_user').content
print r4

r5=s.post(url+'users', data=payload2, verify=False)
print r5.content
dict_user=json.loads(r5.content)
r6=s.delete(url+'users/'+dict_user['id'])
print r6.content
'''
r3= s.delete(url+'logout')
print r3.content
pass



