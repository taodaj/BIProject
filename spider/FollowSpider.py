#!/bin/python
#coding: utf-8

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
import Queue


from Spider import *
from entity import *







class FollowSpider(Spider):

    def __init__(self,username,password,deduplicator,workQueue,resultQueue,event):
        Spider.__init__(self,username,password)
        self.deduplicator=deduplicator
        self.workQueue=workQueue
        self.resultQueue=resultQueue
        self.event=event


    def run(self):
    #if HTTPError occurs only redo 3 times
        logging.debug(self.name + ' gets into run()')

        redoTimes=0
        
        while redoTimes<3 and self.alive:
            try:
                #if it's the first time fetch uid from queue    
                if redoTimes==0:    
                    uid=self.workQueue.get(False)
                    self.deduplicator.add2Set('follow_uid_visited',uid)
                #get follow list
                followList=self.getfollow(uid)
                #put every uid into candidate Queue
                count=0
                for ele in followList:
                    # get uid of follow
                    candidate=ele['fid']
                    #if uid of follow has not been detected yet
                    if self.deduplicator.existInSet('uid',candidate)==False:
                        #added by 1
                        count+=1
                        #put it to detected uid set(including visited and to be visited uid)
                        self.deduplicator.add2Set('uid',candidate)
                        #add it to stored list
                        obj=FollowRelation()
                        obj.inflate(ele)
                        self.resultQueue.put(obj)
                #when finished, set redoTimes=0
                redoTimes=0
                #logging
                logging.info('spider : '+self.name+' detected '+str(count)+' new user ids')
            #redo if it's HTTPError
            except urllib2.HTTPError as e:
                if redoTimes>3:
                    redoTimes=0
                    logging.warning(str(e))
                    logging.warning('spider '+self.name+' try more than 3 times, now give up collecting user : '+uid)
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
