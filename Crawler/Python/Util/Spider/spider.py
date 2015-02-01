#-*- coding: UTF-8 -*-
# #!/bin/python
#fileName:spider.py

import cookielib
import urllib
import urllib2
import pyquery
import logging
import time
import random
import sys

logging.basicConfig(level=logging.DEBUG,  
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',  
                    datefmt='%a, %d %b %Y %H:%M:%S',  
                    stream=sys.stdout  
                    ) 


class BlockedException(Exception):
    def __init__(self):
        Exception.__init__(self)

class spider:
    def __init__(self,username,password):
        self.username=username
        self.password=password
        try: 
            #login and build opener with cookie
            self.opener=self.login()
        except urllib2.HTTPError as e:
            print e
            exit()
        except Exception as e:
            print e
            exit()

    def login(self):
        #create cookie
        cookieJ = cookielib.CookieJar()
        #install cookie
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJ))
        #pretend to be a browser
        opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.65 Safari/537.36')]
        #open login page
        response=opener.open('http://login.weibo.cn/login/')
        loginText=response.read()
        Pyquery=pyquery.PyQuery(loginText)
        #get login url
        loginURL=Pyquery('form').attr('action')
        loginURL='http://login.weibo.cn/login/'+loginURL
        #get password key   
        password=Pyquery('input').eq(1)
        password=pyquery.PyQuery(password).attr('name')
        #get vk value
        vk=Pyquery('input').eq(6).val()
        #wrap post data 
        data={'mobile':self.username,password:self.password,'remember':'on','vk':vk,'submit':'登录'}    
        #encode post data
        data=urllib.urlencode(data)
        #login
        response=opener.open(loginURL,data)
        #<DEBUG>print response.geturl()
        if 'http://login.weibo.cn/' in response.geturl() :
            raise Exception("username or password is wrong")
        logging.info("user :"+self.username+" login sucesses")
        return opener

    def downloadHTML(self,url,expectedURLSeg):
        #HTTPError may be raised       
        req=self.opener.open(url,timeout=5)
        # if blocked by sina, raise exception
        self.blockedCheck(expectedURLSeg,req.geturl())
        #fetch data
        content=req.read()
        #rest for some time
        restTime=self.randomRest()
        #logging
        logging.info('rested for '+str(int(restTime))+'s after collecting data from '+url)
        
        return content
            
    def blockedCheck(self,expectedURL,actualURL):
        if expectedURL not in actualURL:
            logging.info('user : '+self.username+' is blocked by Sina')
            raise BlockedException()

    def randomRest(self):
        restTime=random.random()*2+5
        time.sleep(restTime)
        return restTime


if __name__ == '__main__':
    spider = spider('18612986170', '18612986170')
