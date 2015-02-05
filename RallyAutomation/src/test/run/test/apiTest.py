'''
Created on Feb 3, 2015

@author: ljiang
'''
import requests
import pycurl

#s=requests.session()
#login_data={'formPosted':'1', 'login_email':'me@example.com, 'password':'pw'}
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

url = "http://10.61.40.102/"

s = requests.session()
#r = s.get(url,verify = False)


payload = {
'user[email]':'nonexist@spirent.com',
'user[password]':'spirent'
}
r = s.post(url+'login',data=payload,verify = False)

r2=s.get(url+'current_user')

r3= s.delete(url+'logout')

pass

