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
import HTMLParser
import re
from Spider import *
from lxml import etree

#使用utf-8编码
reload(sys)
sys.setdefaultencoding("utf-8")

#配置日志
logging.basicConfig(level=logging.DEBUG,  
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',  
                    datefmt='%a, %d %b %Y %H:%M:%S',  
                    stream=sys.stdout  
                    ) 



#微博用户信息爬虫
class ProfileSpider(Spider):
    def __init__(self,username,password):
        Spider.__init__(self,username,password)        

    def getProfile(self,uid):
        #生成用户信息的url
        url='http://weibo.cn/'+uid   
        expectedURLSeg='weibo.cn/'+uid
        #初始化信息
        content=''
        infoList=[]
        #如果未得到对应信息（即被反爬虫），重新获取。若5次都失败，则放弃。
        for i in range(0,5,1):
            try:
                print 'uid:',uid  
                #获取对应网址的content
                content=self.downloadHTML(url,expectedURLSeg)  
                #提取微博数、粉丝数、关注人数
                self.extractNumInfo(content);
                #生成用户资料页面的url
                url='http://weibo.cn/'+uid+'/info'
                expectedURLSeg='weibo.cn/'+uid+'/info'
                #获取对应网址的content
                content=self.downloadHTML(url,expectedURLSeg)  
                #提取其他的个人信息
                self.extractInfo(content);
                self.obj['uid']=uid                 
                infoList.append(self.obj)
                return infoList
            #信息提取失败，将信息记入日志，重新提取
            except IndexError as e:
                #logging
                logging.warning('index out, try again from '+url) 
                continue                
        return infoList

    #提取微博数、粉丝数、关注人数的函数
    def extractNumInfo(self,content):
        self.obj={}
        #将html内容变成xpath能处理的tree
        tree=etree.HTML(content)
        try: 
            #针对微博的反爬虫机制，获取到信息块的正确位置
            self.placeNum=2
            while True:  
                if len(tree.xpath('/html/body/div['+str(self.placeNum)+']/div/span/text()')) != 0:
                    break
                else:
                    self.placeNum=self.placeNum+1
            #提取微博数
            weiboNum=tree.xpath('/html/body/div['+str(self.placeNum)+']/div/span/text()')[0][3:-1]
            self.obj['weiboNum']=weiboNum
            print '微博数:',weiboNum
            #提取关注数
            followingNum=tree.xpath('/html/body/div['+str(self.placeNum)+']/div/a[1]/text()')[0][3:-1]
            self.obj['followingNum']=followingNum
            print '关注数:',followingNum
            #提取粉丝数
            fansNum=tree.xpath('/html/body/div['+str(self.placeNum)+']/div/a[2]/text()')[0][3:-1]
            self.obj['fansNum']=fansNum
            print '粉丝数:',fansNum
        except AttributeError as e:
            print e 

    #提取其他信息的函数
    def extractInfo(self,content):
        #将html内容变成xpath能处理的tree
        tree=etree.HTML(content)
        #提取微博等级
        level=tree.xpath('/html/body/div['+str(self.placeNum+1)+']/a[1]/text()')[0][:-1]
        self.obj['level']=level
        print '微博等级:',level
        #提取会员等级
        vipLevel=tree.xpath('/html/body/div['+str(self.placeNum+1)+']/text()')[1][5:-2]
        if ('未开' in vipLevel): 
            vipLevel='null'
        self.obj['vipLevel']=vipLevel
        print '会员等级:',vipLevel
        #初始化变量
        name='null'
        location='null'
        gender='null'
        birthday='null'
        intro='null'
        identifyContent='null'
        labels=[]
        education=[]
        job=[]
        #获取信息块    
        infoArray=tree.xpath('/html/body/div['+str(self.placeNum+3)+']/text()')
        #对信息块遍历，提取相应信息
        for ele in infoArray:
            label=ele[0:2]            
            if cmp(label,'昵称') ==0:    
                name=ele[3:]
            if cmp(label,'认证') ==0:    
                identifyContent=ele[5:] 
            if cmp(label,'性别') ==0:    
                gender=ele[3:]  
            if cmp(label,'地区') ==0:    
                location=ele[3:]  
            if cmp(label,'生日') ==0:    
                birthday=ele[3:] 
            if cmp(label,'简介') ==0:    
                intro=ele[3:]  
            if cmp(label,'标签') ==0:    
                labelArray=tree.xpath('/html/body/div['+str(self.placeNum+3)+']/a/text()')
                count=1
                for ele1 in labelArray:
                    if ('更多' in ele1): 
                        continue
                    labels.append(ele1)
                    print 'label:',ele1
        self.obj['name']=name
        print 'name:',name
        self.obj['gender']=gender
        print 'gender:',gender
        self.obj['location']=location
        print 'location:',location
        self.obj['birthday']=birthday
        print 'birthday:',birthday
        self.obj['intro']=intro
        print 'intro:',intro
        self.obj['identifyContent']=identifyContent
        print 'identifyContent:',identifyContent
        self.obj['label']=label
        #获取工作经历、学习经历的提示信息
        inferInfo=tree.xpath('/html/body/div['+str(self.placeNum+4)+']/text()')
        #如果该提示信息是学习经历，则提取学习经历
        if cmp(inferInfo[0],'学习经历') ==0:
            #获取学习经历信息块
            eduInfo=tree.xpath('/html/body/div['+str(self.placeNum+5)+']/text()')
            #对学习信息块进行遍历，提取每一条学习经历信息
            for ele in eduInfo:
                self.obj['education']=ele
                print 'education:',ele
            #获取工作经历的提示信息
            inferInfo=tree.xpath('/html/body/div['+str(self.placeNum+6)+']/text()')
            #如果该提示信息是工作经历，则提取工作经历(这里是在有学习经历的情况下进行提取)
            if cmp(inferInfo[0],'工作经历') ==0:
                #获取工作经历信息块
                proInfo=tree.xpath('/html/body/div['+str(self.placeNum+7)+']/text()')
                #对工作信息块进行遍历，提取每一条工作经历信息
                for ele in proInfo:
                    pro=HTMLParser.HTMLParser().unescape(ele)
                    job.append(ele)
                    self.obj['job:']=ele
                    print 'job:',ele
        #获取工作经历的提示信息
        inferInfo=tree.xpath('/html/body/div['+str(self.placeNum+4)+']/text()')
        #如果该提示信息是工作经历，则提取工作经历(这里是没有学习经历的情况下进行提取)
        if cmp(inferInfo[0],'工作经历') ==0:
            #获取工作经历信息块
            proInfo=tree.xpath('/html/body/div['+str(self.placeNum+5)+']/text()')
            #对工作信息块进行遍历，提取每一条工作经历信息
            for ele in proInfo:
                pro=HTMLParser.HTMLParser().unescape(ele)
                job.append(ele)
                self.obj['job:']=ele
                print 'job:',ele
        self.obj['education']=education
        self.obj['job']=job         


        

    
if __name__ == '__main__':
    #!!!!USE YOUR USERNAME AND PASSWORD HERE
    spider = ProfileSpider('564257051@qq.com', '123123123')
    count=1     
    file = open("test-uids")
    spider.getProfile('1496846867')
    while 1:
        line = file.readline()
        if not line:
            break
        pass # do something
        print count
        uid=line[0:10]
        count=count+1
        spider.getProfile(uid)

