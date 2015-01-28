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
from spider import spider


logging.basicConfig(level=logging.DEBUG,  
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',  
                    datefmt='%a, %d %b %Y %H:%M:%S',  
                    stream=sys.stdout  
                    ) 



class BlockedException(Exception):
    def __init__(self):
        Exception.__init__(self)

class followingSpider(spider):
    def __init__(self,username,password):
        spider.__init__(self,username,password)        

    #get the users he follows
    def getfollowing(self,userid):
        #list to store the people he follows
        followingList=[]
        
        #HTTPError may be raised
        req=self.opener.open('http://weibo.cn/'+userid+'/follow',timeout=5)
        # if blocked by sina, raise exception
        self.blockedCheck('weibo.cn/'+userid+'/follow',req.geturl())
        content=req.read()
        followingList.extend(self.extractFollowing(userid,content))    

        #rest for a while
        restTime=self.randomRest()
        #logging
        logging.info('rested for '+str(restTime)+' collect from '+req.geturl())
        #extract next url
        while True:
            nextUrl=self.extractFollowingUrl(content)
            if nextUrl == None:
                break
            req=self.opener.open('http://weibo.cn'+nextUrl,timeout=5)
            self.blockedCheck('weibo.cn/'+userid+'/follow',req.geturl())
            try:
                content=req.read()
                #extract data
                followingList.extend(self.extractFollowing(userid,content))
                #rest for a while
                restTime=self.randomRest()
                #logging
                logging.info('rested for '+str(restTime)+' collect from '+req.geturl())
            except socket.timeout as e:
                #logging
                logging.info('TIME OUT, try again from '+req.geturl())
                continue 

        return followingList

    def blockedCheck(self,expectedURL,actualURL):
        if expectedURL not in actualURL:
            logging.info('user : '+self.username+' is blocked by Sina')
            raise BlockedException()
    
    def randomRest(self):
        restTime=random.random()*2+5
        time.sleep(restTime)
        return restTime     
    
    def extractFollowingUrl(self,content):
        html=pyquery.PyQuery(content)
        for ele in html('form a'):
            if pyquery.PyQuery(ele).text()=='下页':
                return pyquery.PyQuery(ele).attr('href')
        return None

    #ATTENTION: Here assume spider follows nobody
    def extractFollowing(self,userid,content):
        pageList=[]
        html=pyquery.PyQuery(content)
        for ele in html('table'):
            try:
                name=pyquery.PyQuery(ele)('td').eq(1)('a').eq(0).text()
                uid=pyquery.PyQuery(ele)('td').eq(1)('a').eq(1).attr('href').split('?')[1].split('&')[0].split('=')[1]
                fans=pyquery.PyQuery(ele)('td').text().split(' ')[1][2:-1]
                pageList.append(userid+','+uid+','+name+','+fans)
            except AttributeError as e:
                print e 
                continue
        return pageList

if __name__ == '__main__':
    #!!!!USE YOUR USERNAME AND PASSWORD HERE
    spider = weiboSpider('USERNAME', 'PASSWORD')
    print spider.getfollowing('3399558022')
