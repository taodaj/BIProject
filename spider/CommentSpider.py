#!/bin/python
#coding: utf-8


import logging
import sys
import socket
import urllib2 
import threading
#  'ascii' codec can't encode characters
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import Queue

from lxml import etree
import re
import pyquery
import time,datetime
import HTMLParser

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from Spider import *
from entity import *







class CommentSpider(Spider):

    def __init__(self,username,password,deduplicator,workQueue,resultQueue,event):
        Spider.__init__(self,username,password)     
        self.deduplicator=deduplicator
        self.workQueue=workQueue
        self.resultQueue=resultQueue
        self.event=event
        self.incrmt_flag = False
        

    def run(self):
    #if HTTPError occurs only redo 3 times
        logging.debug(self.name + ' gets into run()')
        redoTimes=0
        
        while redoTimes<3 and self.alive:
            try:
                #if it's the first time, fetch uwid from queue    
                if redoTimes==0:    
                    uwid=self.workQueue.get(False).split(',')
                    self.deduplicator.add2Set('comment_uwid_visited',uwid[0]+','+uwid[1])

                #get comment list
                commentList=self.getComment(uwid[0],uwid[1])

                count=0
                for ele in commentList:
                    # get wid of follow
                    candidate=ele['wid']+','+ele['cid']
                    #put all wcid detected into 'wcid' set
                    if self.deduplicator.existInSet('wcid',candidate)==False:
                        #added by 1
                        count+=1       
                        self.deduplicator.add2Set('wcid',candidate)
                        #add it to result queue
                        obj=Comment()
                        obj.inflate(ele)
                        self.resultQueue.put(obj)
                #when finished, set redoTimes=0
                redoTimes=0
                #logging
                logging.info('spider : '+self.name+' detected '+str(count)+' new comments')
            #redo if it's HTTPError
            except urllib2.HTTPError as e:
                if redoTimes>3:
                    redoTimes=0
                    logging.warning(str(e))
                    logging.warning('spider '+self.name+' try more than 3 times, give up collecting from wcid : '+candidate)
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



    # get weibo comment
    def getComment(self, userid,weiboid):
        #list to store the people he follows
        self.userid=userid
        self.weiboid=weiboid
        commentList = []

        preURL = 'http://weibo.cn/'
        postURL = 'comment/'+weiboid + '?uid=' + userid + '&rl=2&page=1'
        expectedURLSeg='comment/'+weiboid + '?uid=' + userid

        while True:
            #HTTPError AND TIMEOUT , BlockedException may arise
            content=self.downloadHTML(preURL+postURL,expectedURLSeg)
            #extract data
            tree=etree.HTML(content)

            #increment
            if self.incrmt_flag == True:
                break

            commentList.extend(self.extractComment(tree))
            #extract next url
            postURL=self.extractFollowUrl(content)
            if postURL == None:
                break

        return commentList



    def extractFollowUrl(self,content):
        html=pyquery.PyQuery(content)
        for ele in html('form a'):
            if pyquery.PyQuery(ele).text()==u'下页':
                return pyquery.PyQuery(ele).attr('href')
        return None


    def extractComment(self, tree):
        commentList = []
        idList = tree.xpath('//div/@id')

        for cid in idList:
            
            if(cid == self.deduplicator.hashGet('latest_comment',self.weiboid)):
                self.incrmt_flag = True
                return commentList
            
            if(re.match('C_',cid)):
                self.deduplicator.hashSet('latest_comment',self.weiboid,cid)
                xpath_comment='//div[@id="'+cid+'"]'+'/span[@class="ctt"]'
                xpath_comment_text='//div[@id="'+cid+'"]'+'/span[@class="ctt"]/text()'
                xpath_comment_at = '//div[@id="'+cid+'"]'+'/span[@class="ctt"]/a/text()'
                xpath_time='//div[@id="'+cid+'"]'+'/span[@class="ct"]/text()'
                xpath_agree='//div[@id="'+cid+'"]'+'/span[@class="cc"][1]/a/text()'
                #comment 评论内容
                comment = str(tree.xpath('string('+xpath_comment+')'))
                #agree 赞同数
                agree=str(tree.xpath(xpath_agree)[0][2])
                timearray=tree.xpath(xpath_time)[0].encode('utf-8').split('来自')[0].split(' ')

                time_sent = str(self.timeFormat(timearray))

                #print type(self.userid),type(self.weiboid),type(comment),type(agree),type(time_sent),type(cid)
                commentContent = {'uid':self.userid,'wid':self.weiboid,'comment':comment,'agree':agree,'time':time_sent,'cid':str(cid)}
                commentList.append(commentContent)
                print commentContent
                logging.debug(commentContent)

        return commentList

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
        return unicode(time_sent,'utf8')
