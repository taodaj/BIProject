#!/bin/python
# -*- coding: utf-8 -*-

import cookielib
import urllib
import urllib2
import pyquery
import logging
import time
import random
import socket
import sys
import spider as Spider
from lxml import etree
import re

reload(sys)
sys.setdefaultencoding("utf-8")

logging.basicConfig(level=logging.DEBUG,  
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',  
                    datefmt='%a, %d %b %Y %H:%M:%S',  
                    stream=sys.stdout  
                    ) 


class profileSpider(Spider.spider):
    def __init__(self,username,password):
        Spider.spider.__init__(self,username,password)        

    #get the users he follows
    def getProfile(self,userid):
        url='http://weibo.cn/'+userid   
        expectedURLSeg='weibo.cn/'+userid    
        content=''
        for i in range(0,5):
            try:
                #HTTPError AND TIMEOUT , BlockedException may arise
                content=self.downloadHTML(url,expectedURLSeg)
                #extract data about weibonum, followernum, fansnum
                userinfo=self.extractNumInfo(userid,content);
                tree=etree.HTML(content)
                url='http://weibo.cn/'+userid+'/info'
                expectedURLSeg='weibo.cn/'+userid+'/info'
                #HTTPError AND TIMEOUT , BlockedException may arise
                content=self.downloadHTML(url,expectedURLSeg)  
                #extract other data
                userinfo=userinfo+self.extractInfo(userid,content);    
                return userinfo
            except socket.timeout as e:
                #logging
                logging.warning('TIME OUT, try again from '+url) 
                continue
            except IndexError as e1:
                #logging
                logging.warning('index out, try again from '+url) 
                continue                
        return ''
    
    def extractNumInfo(self,userid,content):
        html=pyquery.PyQuery(content)
        tree=etree.HTML(content)
        try:
            self.placeNum=2
            while True:  
                if len(tree.xpath('/html/body/div['+str(self.placeNum)+']/div/span/text()')) != 0:
                    break
                else:
                    self.placeNum=self.placeNum+1
            weiboNum=tree.xpath('/html/body/div['+str(self.placeNum)+']/div/span/text()')[0][3:-1]
            followingNum=tree.xpath('/html/body/div['+str(self.placeNum)+']/div/a[1]/text()')[0][3:-1]
            fansNum=tree.xpath('/html/body/div['+str(self.placeNum)+']/div/a[2]/text()')[0][3:-1]
            numInfo=userid+','+weiboNum+','+followingNum+','+fansNum
            return numInfo
        except AttributeError as e:
            print e 
            return ''
    
    def strFormatTrans(self,str):
        s=str.replace(',','.')
        s=s.replace('\n','.') 
        return s

    #ATTENTION: Here assume spider follows nobody
    def extractInfo(self,userid,content):
        html=pyquery.PyQuery(content)
        tree=etree.HTML(content)
        level=tree.xpath('/html/body/div['+str(self.placeNum+1)+']/a[1]/text()')[0][:-1]
        vipLevel=tree.xpath('/html/body/div['+str(self.placeNum+1)+']/text()')[1][5:-2]
        if ('未开' in vipLevel): 
            vipLevel='null'
        name='null'
        location='null'
        gender='null'
        birthday='null'
        intro='null'
        identifyContent='null'
        label1='null'
        label2='null'
        label3='null'    
        infoArray=tree.xpath('/html/body/div['+str(self.placeNum+3)+']/text()')
        
        for ele in infoArray:
            label=ele[0:2]            
            if cmp(label,'昵称') ==0:    
                name=ele[3:]
                name=self.strFormatTrans(name)
            if cmp(label,'认证') ==0:    
                identifyContent=ele[5:]
                identifyContent=self.strFormatTrans(identifyContent)  
            if cmp(label,'性别') ==0:    
                gender=ele[3:]  
                gender=self.strFormatTrans(gender)
            if cmp(label,'地区') ==0:    
                location=ele[3:]  
                location=self.strFormatTrans(location)
            if cmp(label,'生日') ==0:    
                birthday=ele[3:] 
                birthday=self.strFormatTrans(birthday)  
            if cmp(label,'简介') ==0:    
                intro=ele[3:]  
                intro=self.strFormatTrans(intro) 
            if cmp(label,'标签') ==0:    
                labelArray=tree.xpath('/html/body/div['+str(self.placeNum+3)+']/a/text()')
                count=1
                for ele1 in labelArray:
                    if ('更多' in ele1): 
                        continue
                    if count==1:
                        label1=ele1;
                        label1=self.strFormatTrans(label1) 
                    if count==2:
                        label2=ele1;
                        label2=self.strFormatTrans(label2) 
                    if count==3:
                        label3=ele1;
                        label3=self.strFormatTrans(label3)
                    count=count+1
            
        info=','+level+','+vipLevel+','+name+','+gender+','+location+','+birthday+','+intro+','+identifyContent+','+label1+','+label2+','+label3
        print info
        return info

if __name__ == '__main__':
    #!!!!USE YOUR USERNAME AND PASSWORD HERE
    Spider.spider = profileSpider('564257051@qq.com','123123123')
    count=1     
    file = open("test-uids")
    while 1:
        line = file.readline()
        if not line:
            break
        pass # do something
        print count
        uid=line[0:10]
        print uid
        count=count+1
        Spider.spider.getProfile(uid)
    print 1
    print Spider.spider.getProfile('1219461122')
    print 2
    print Spider.spider.getProfile('1906933201')
    print 3
    print Spider.spider.getProfile('1462649411')
    print 4
    print Spider.spider.getProfile('1210949137')
    print 5
    print Spider.spider.getProfile('233178940')
    print 6
    print Spider.spider.getProfile('206264040')
    print 1
    print Spider.spider.getProfile('1887826884')
    print 2
    print Spider.spider.getProfile('3217179555')
    print 3
    print Spider.spider.getProfile('1713926427')
    print 4
    print Spider.spider.getProfile('3578479905')
    print 5
    print Spider.spider.getProfile('1195366567')
    print 6
    print Spider.spider.getProfile('233178940')
 


