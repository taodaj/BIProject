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
from spider import spider
from spider import BlockedException

logging.basicConfig(level=logging.DEBUG,  
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',  
                    datefmt='%a, %d %b %Y %H:%M:%S',  
                    stream=sys.stdout  
                    ) 


#####
#   structure of fanslist  |user id|fans id|fans name|fansNum of fans|
#####

class fansSpider(spider):
    def __init__(self,username,password):
        spider.__init__(self,username,password)        

    #get the users following him
    def getfans(self,userid):
        #list to store the people following him
        fansList=[]
        content=''
        preURL='http://weibo.cn'
        postURL='/'+userid+'/fans'
        expectedURLSeg='weibo.cn/'+userid+'/fans'
        while True:
            try:
                #HTTPError AND TIMEOUT , BlockedException may arise
                content=self.downloadHTML(preURL+postURL,expectedURLSeg)
                #extract data
                fansList.extend(self.extractFans(userid,content))
                #extract next url
                postURL=self.extractFansUrl(content)
                if postURL == None:
                    break
            except socket.timeout as e:
                #logging
                logging.warning('TIME OUT, try again from '+postURL)
                continue


        return fansList

    
    
    def extractFansUrl(self,content):
        html=pyquery.PyQuery(content)
        for ele in html('form a'):
            if pyquery.PyQuery(ele).text()=='下页':
                return pyquery.PyQuery(ele).attr('href')
        return None

    #ATTENTION: Here assume spider follows nobody
    def extractFans(self,userid,content):
        pageList=[]
        html=pyquery.PyQuery(content)
        for ele in html('table'):
            try:
                name=pyquery.PyQuery(ele)('td').eq(1)('a').eq(0).text()
                uid=pyquery.PyQuery(ele)('td').eq(1)('a').eq(1).attr('href').split('?')[1].split('&')[0].split('=')[1]
                fans=pyquery.PyQuery(ele)('td').text().split(' ')[1][2:-1]
                pageList.append(userid+','+uid+','+name+','+fans)
            except AttributeError as e:
                logging.warning(str(e))
                continue
        return pageList

if __name__ == '__main__':
    #!!!!USE YOUR USERNAME AND PASSWORD HERE
    spider = fansSpider(USERNAME, PASSWORD)
    print spider.getfans('3399558022')
