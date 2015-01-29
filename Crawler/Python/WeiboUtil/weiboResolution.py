#!/bin/python
# FileName : weiboResolution.py
# -*- coding: utf-8 -*-

import cookielib
import urllib
import urllib2
import pyquery
import logging
import time
import random
import sys
from lxml import etree

sys.path.append('..')
import WeiboElement.weiboInfo as weiboInfo
#import weiboInfo

reload(sys)
sys.setdefaultencoding('utf-8')

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',datefmt='%a, %d %b %Y %H:%M:%S',stream=sys.stdout) 


class BlockedException(Exception):
    def __init__(self):
        Exception.__init__(self)

class weiboResolution:
    def __init__(self,username,password):
        self.username=username
        self.password=password
        

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
        tree=etree.HTML(loginText)
        #get password key	
        password=tree.xpath('//input[@type="password"]/@name')[0]
        #get vk value
        vk=tree.xpath('//input[@name="vk"]/@value')[0]
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

    #get the users' weibo
    def getWeibo(self,userid):
        #weibo list
        weiboList=[]
        #HTTPError may be raised
        req=self.opener.open('http://weibo.cn/'+userid+'?page=0',timeout=5)
        # if blocked by sina, raise exception
        self.blockedCheck('weibo.cn/'+userid+'?page='+weiboid,req.geturl())
        content=req.read()
        #extract data
        followingList.extend(self.extractFollowing(content,userid))
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
                weiboList.extend(self.extractFollowing(content,userid))
                #rest for a while
                restTime=self.randomRest()
                #logging
                logging.info('rested for '+str(restTime)+' collect from '+req.geturl())
            except socket.timeout as e:
                #logging
                logging.info('TIME OUT, try again from '+req.geturl())
                continue 

        return weiboList

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
            if pyquery.PyQuery(ele).text()==u'下页':
                return pyquery.PyQuery(ele).attr('href')
        return None

    #ATTENTION: Here assume spider follows nobody
    def extractFollowing(self,content,userid):
        atsList=[]
        tree=etree.HTML(content)
        #tree=etree.HTML(content)
        i=0
        for ele in tree.xpath(u"//div[@class='c' and @id]"):
            weiboid=ele.get("id").split('_')[1]
            hrefs = ele.xpath(u"div/span[@class='cmt']/a")
            if hrefs:
                fowardingWeiboId=hrefs[0].text
                content=ele.xpath(u"div[last()]/text()")[0]
                ats=ele.xpath(u"div[last()]/a")[0]
            else :
                fowardingWeiboId=" "
                content=ele.xpath(u"div/span[@class='ctt']")[0].text
                ats=ele.xpath(u"div/span[@class='ctt']/a")
            for at in ats:
                strat=at.get('href')
                if strat.find('/n/')!=-1:
                    atsList.append(strat[2:-1])  
            likeNum=ele.xpath(u"div[last()]/a[last()-3]")[0].text
            commentNum=ele.xpath(u"div[last()]/a[last()-1]")[0].text
            fowardingNum=ele.xpath(u"div[last()]/a[last()-2]")[0].text
            info=ele.xpath(u"div[last()]/span[@class='ct']")[0].text.split(u'来自')
            time=info[0]
            plantform=info[1]
            weibo=weiboInfo.weiboInfo(weiboid,userid,content,time,fowardingNum,commentNum,likeNum,plantform)
            if hrefs:
                weibo.setfowardingWeiboId(fowardingWeiboId)
            if len(atsList):
                weibo.setAT(atsList)
            print weiboid+","+fowardingWeiboId+","+likeNum+","+commentNum+","+time+","+plantform+","+fowardingNum 
        return weibo

if __name__ == '__main__':
    spider = weiboResolution('18612986170', '18612986170')
    #print spider.extractFollowing('3399558022')
    spider.extractFollowing(html,'3399558022')
