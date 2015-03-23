#!/bin/python
# -*- coding: utf-8 -*-

import cookielib
import urllib
import urllib2
import pyquery
import logging
import time
import random
import sys
import socket
import threading



class BlockedException(Exception):
    def __init__(self,*args):
        Exception.__init__(self,*args)

class Spider(threading.Thread):
    def __init__(self,username,password):
        threading.Thread.__init__(self)
        self.name=username
        self.password=password
        self.status='normal'
        self.alive=True

        try: 
            #login and build opener with cookie
            self.opener=self.login()
        except urllib2.HTTPError as e:
            print e
            exit()
        except Exception as e:
            print e
            exit()


    def stop(self):
        self.alive=False



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
        data={'mobile':self.name,password:self.password,'remember':'on','vk':vk,'submit':'登录'}    
        #encode post data
        data=urllib.urlencode(data)
        #login
        response=opener.open(loginURL,data)
        #<DEBUG>print response.geturl()
        if 'http://login.weibo.cn/' in response.geturl() :
            raise Exception("username or password is wrong")
        logging.info("user :"+self.name+" login sucesses")
        return opener

    def downloadHTML(self,url,expectedURLSeg):
        while True:
            try:
                #HTTPError may be raised       
                req=self.opener.open(url,timeout=5)
                # if blocked by sina, raise exception
                self.blockedCheck(expectedURLSeg,req.geturl())
                #fetch data
                content=req.read()
                #rest for some time
                restTime=self.randomRest()
                #logging
                logging.info('spider '+self.name+' rested for '+str(int(restTime))+'s after collecting data from '+url) 
                return content
            except socket.timeout as e:
                #if time out, rest for sometime and then try to open url again
                restTime=self.randomRest()
                logging.warning('TIME OUT,'+' spider '+self.name+' try again from '+url)
                continue
            
    def blockedCheck(self,expectedURL,actualURL):
        if expectedURL not in actualURL:
            logging.info('spider : '+self.name+' is blocked by Sina')
            raise BlockedException()

    def randomRest(self):
        restTime=random.random()*5+5
        time.sleep(restTime)
        return restTime


