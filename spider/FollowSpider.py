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
from Spider import *






class FollowSpider(Spider):
    def __init__(self,username,password):
        Spider.__init__(self,username,password)        

    #get the users he follows
    def getfollow(self,userid):
        #list to store the people he follows
        followList=[]
        content=''
        preURL='http://weibo.cn'
        postURL='/'+userid+'/follow'
        expectedURLSeg='weibo.cn/'+userid+'/follow'
        while True:
            #HTTPError AND TIMEOUT , BlockedException may arise
            content=self.downloadHTML(preURL+postURL,expectedURLSeg)
            #extract data
            followList.extend(self.extractFollow(userid,content))
            #extract next url
            postURL=self.extractFollowUrl(content)
            if postURL == None:
                break

        return followList

    
    
    def extractFollowUrl(self,content):
        html=pyquery.PyQuery(content)
        for ele in html('form a'):
            if pyquery.PyQuery(ele).text()=='下页':
                return pyquery.PyQuery(ele).attr('href')
        return None

    #ATTENTION: Here assume spider follows nobody
    def extractFollow(self,userid,content):
        pageList=[]
        html=pyquery.PyQuery(content)
        for ele in html('table'):
            try:
                obj={}
                name=pyquery.PyQuery(ele)('td').eq(1)('a').eq(0).text()
                uid=pyquery.PyQuery(ele)('td').eq(1)('a').eq(1).attr('href').split('?')[1].split('&')[0].split('=')[1]
                fans=pyquery.PyQuery(ele)('td').text().split(' ')[1][2:-1]
                
                obj['uid']=userid
                obj['name']=name
                obj['fid']=uid
                obj['fans']=fans

                pageList.append(obj)

            except AttributeError as e:
                logging.warning(str(e))
                continue
        return pageList
