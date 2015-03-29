# FileName : weiboSpider.py
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
from lxml import etree
import datetime
import threading
import Queue


from Spider import *
from entity import *



class WeiboSpider(Spider):
    def __init__(self,username,password,deduplicator,workQueue,resultQueue,event):
        Spider.__init__(self,username,password)
        self.deduplicator=deduplicator
        self.workQueue=workQueue
        self.resultQueue=resultQueue
        self.event=event
        self.checkFirstWeibo = False
        self.checkSaveWeibo = False


    def run(self):
    #if HTTPError occurs only redo 3 times
        logging.debug(self.name + ' gets into run()')
        redoTimes=0
        
        while redoTimes<3 and self.alive:
            try:
                #if it's the first time fetch uid from queue    
                if redoTimes==0:    
                    uid=self.workQueue.get(False)
                    self.deduplicator.add2Set('weibo_uid_visited',uid)
                #get weibo list
                weiboList=self.getWeibo(uid)
                count=0
                for ele in weiboList:
                    # get wuid 
                    candidate=ele['uid']+','+ele['wid']
                    #if this weibo hasnt been collected before
                    if self.deduplicator.existInSet('uwid',candidate)==False:
                        #added by 1
                        count+=1       
                        self.deduplicator.add2Set('uwid',candidate)
                        #add it to stored list
                        obj=Weibo()
                        obj.inflate(ele)
                        self.resultQueue.put(obj)
                #when finished, set redoTimes=0
                redoTimes=0
                #logging
                logging.info('spider : '+self.name+' detected '+str(count)+' new weibo')
            #redo if it's HTTPError
            except urllib2.HTTPError as e:
                if redoTimes>3:
                    redoTimes=0
                    logging.warning(str(e))
                    logging.warning('spider '+self.name+' try more than 3 times, now give up collecting weibo : '+candidate)
                else:
                    redoTimes+=1


            except BlockedException as e:
                logging.info('spider '+self.name+' is blocked by Sina')
                self.status='blocked'
                break


            except urllib2.URLError as e:
                #network error, no internet available
                raise e
            
            except Queue.Empty as e:
                self.event.clear()
                logging.info('spider : '+self.name+' waits for resource')
                self.event.wait()
                logging.info('spider : '+self.name+' restarts')


    #get the users' weibo
    def getWeibo(self,userid):
        #weibo list
        weiboList=[]
        content=''
        self.checkFirstWeibo=False
        self.checkSaveWeibo = False
        preURL='http://weibo.cn'
        postURL='/u/'+userid
        expectedURLSeg='weibo.cn/u/'+userid
        while True:
           #HTTPError AND TIMEOUT , BlockedException may arise
           content=self.downloadHTML(preURL+postURL,expectedURLSeg)
           #extract data
           weiboList.extend(self.extractFollowing(content,userid))
           #extract next url
           postURL=self.extractFollowingUrl(content)
           if postURL == None:
              #print 'Cant get postURL'
              break
           if self.checkFirstWeibo:
               break;
        return weiboList

    def extractFollowingUrl(self,content):
        self.checkSaveWeibo=True
        tree=etree.HTML(content)
        for ele in tree.xpath(u"//div[@class='pa' and @id='pagelist']"):
            if ele.xpath(u"form/div/a")[0].text==u'下页':
                return ele.xpath(u"form/div/a")[0].get("href")
        return None

    #ATTENTION: Here assume spider follows nobody
    def extractFollowing(self,contents,userid):
        pageList=[]
        tree=etree.HTML(contents)
        i=0
        for ele in tree.xpath(u"//div[@class='c' and @id]"):
            try:
                obj={}
                weiboid=ele.get("id").split('_')[1]
                if(self.checkSaveWeibo==False):
                    self.deduplicator.hashSet('latest_weibo',userid,weiboid)
                if(weiboid==self.deduplicator.hashGet('latest_weibo',userid)):
                    self.checkFirstWeibo = True
                    return pageList
                #print weiboid
                hrefs = ele.xpath(u"div/span[@class='cmt']/a")
                fowardingWeiboId=""
                atsList=""
                content=""
                if hrefs:
                    fowardingWeiboId=hrefs[0].text
                    contentList=ele.xpath(u"div[last()]/text()")
                    for contents in contentList:
                        content+=contents
                    ats=ele.xpath(u"div[last()]/a")[0]
                else :
                    contentList=ele.xpath(u"div/span[@class='ctt']/text()")
                    for contents in contentList:
                        content+=contents
                    ats=ele.xpath(u"div/span[@class='ctt']/a")
                for at in ats:
                    strat=at.get('href')
                    if strat.find('/n/')!=-1:
                        atsList+=at.text[1:]+"//"
                #print content
                likeNum=ele.xpath(u"div[last()]/a[last()-3]")[0].text
                commentNum=ele.xpath(u"div[last()]/a[last()-1]")[0].text
                fowardingNum=ele.xpath(u"div[last()]/a[last()-2]")[0].text
                info=ele.xpath(u"div[last()]/span[@class='ct']")[0].text.split(u'来自')
                timearray=info[0].split(' ')
                time_sent = str(self.timeFormat(timearray))
                plantform=info[1]
                if type(content) == type(None):
                    logging.warning('Did not get '+weiboid+'content ')
                    content= " "
                #print time_sent
                obj['wid']=weiboid
                obj['uid']=userid
                obj['content']=content
                obj['time_sent']=time_sent
                obj['fowardingNum']=fowardingNum
                obj['commentNum']=commentNum
                obj['likeNum']=likeNum
                obj['plantform']=plantform
                obj['fowardingWeiboId']=fowardingWeiboId
                obj['atsList']=atsList
                pageList.append(obj)
                logging.debug(weiboid+','+userid+','+content+','+time_sent+','+fowardingNum+','+commentNum +','+likeNum+','+plantform+','+fowardingWeiboId+','+atsList)
            except AttributeError as e:
                logging.warning(str(e))
                continue
        return pageList
    #统一时间格式
    def timeFormat(self,timearray):

        if(len(timearray)==2):
            #eg 今天 21:59
            if(timearray[0]=="今天"):
                date_weibo = time.strftime('%Y-%m-%d',time.localtime(time.time()))
                time_weibo = timearray[1]
            #eg 2014-12-31 13:38:16
            elif(timearray[0].find('-') >= 0):
                time_hour = timearray[1].split(':')[0]
                time_min = timearray[1].split(':')[1]
                date_weibo = timearray[0]
                time_weibo = time_hour+':'+time_min

            #eg  01月02日 01:37
            elif(timearray[0].find('月') >= 0):
                time_month = timearray[0].split('月')[0]
                time_day = timearray[0].split('月')[1].split('日')[0]
                time_year = time.strftime('%Y',time.localtime(time.time()))
                time_weibo = timearray[1]
                date_weibo = time_year+'-'+time_month+'-'+time_day

            time_sent = date_weibo+' '+time_weibo
        #eg 1分钟前
        elif(len(timearray)==1):
            minute_ago = int(timearray[0].split('分钟前')[0])
            date_now = datetime.datetime.fromtimestamp(time.time())
            date_time_sent = date_now - datetime.timedelta(minutes=minute_ago)
            time_sent = datetime.datetime.strftime(date_time_sent,'%Y-%m-%d %H:%M')
        return time_sent