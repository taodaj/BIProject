#!/bin/python
# -*- coding: utf-8 -*-

import Queue
import urllib2
import sys
import logging
import pickle
import os
from Spider import *
from Entity import *
import util
from storage import storage

reload(sys)
sys.setdefaultencoding("utf-8")

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    stream=sys.stdout
                    )

class dispatcher:
    '''
    In this version, dispatcher can only handle single spider, that is, it is still single thread program
    '''
 
    def __init__(self):
        #MODIFY HERE!!!!!
        self.STORESIZE=100
        #candidate queue which spider fetches uid from
        self.candidateQueue=Queue.Queue()
        self.accounts=Queue.Queue()
        #list to keep objs
        self.storedList=[]
        # storage Class
        self.storage=storage()
        #deduplicator Class
        self.deduplicator=util.Deduplicator()



    def dispatch(self,type):
        self.initAccount()
        #self.initCandidate('Weibo')
        #self.initCandidate('Profile')
        #self.initCandidate('Comment')
        self.initCandidate(type)
        ac=self.accounts.get()
        if type=='FollowRelation':
            self.collectWeibo(ac['username'],ac['password'])
        elif type=='Profile':
            self.collectProfile(ac['username'],ac['password'])
        elif type=='Weibo':
            self.collectWeibo(ac['username'],ac['password'])
        elif type=='Comment':
            self.collectComment(ac['username'],ac['password'])


    def initCandidate(self,type,sourceDir=None):
        if sourceDir==None:
            sourceDir=os.getcwd()+os.sep+'ids'
        filelist=os.listdir(sourceDir)       

        if type=='Comment':
            #set up uid list to record whether the responding weibo info is fetched
            self.deduplicator.setup('comment_uwid')
            for file in filelist:
                if file.startswith('uwid'):
                    f=open(sourceDir+os.sep+file,'r') 
                    for line in f:
                        line=line[:-1]
                        if self.deduplicator.existInSet('comment_uwid',line)==False:
                            line=line.split(',')
                            m=[]
                            #append uid
                            m.append(line[0])
                            #append wid
                            m.append(line[1])
                            self.candidateQueue.put(m)
                    f.close()
        
        elif type=='FollowRelation':
            f=open(sourceDir+os.sep+'startpoint','r')
            #set up uid list to record whether the responding ids info is fetched
            self.deduplicator.setup('followRelation_uid')
            for line in f:
                line=line[:-1]
                if self.deduplicator.existInSet('followRelation_uid',line)==False:
                    self.candidateQueue.put(line)
            f.close()

        elif type=='Weibo':
            #set up uid list to record whether the responding weibo info is fetched
            self.deduplicator.setup('weibo_uid')
            for file in filelist:
                if file.startswith('uid'):
                    f=open(sourceDir+os.sep+file,'r')           
                    for line in f:
                        line=line[:-1]
                        if self.deduplicator.existInSet('weibo_uid',line)==False:
                            self.candidateQueue.put(line)
                    f.close()

        elif  type =='Profile':
            #set up uid list to record whether the responding profile info is fetched
            self.deduplicator.setup('profile_uid')
            for file in filelist:
                if file.startswith('uid'):
                    f=open(sourceDir+os.sep+file,'r')  
                    for line in f:
                        line=line[:-1]
                        if self.deduplicator.existInSet('profile_uid',line)==False:
                            self.candidateQueue.put(line)
                    f.close()
        


    def initAccount(self,source='ids/accounts'):
        f=open(source,'r')
        for line in f:
            line=line[:-1].split(' ')
            m={}
            m['username']=line[0]
            m['password']=line[1]
            self.accounts.put(m)
        f.close()


    def collectFollow(self,username,password):
        #every spider is equiped with an account
        spider=FollowSpider(username,password)
        self.deduplicator.setup('uid')
        #if HTTPError occurs only redo 3 times
        redoTimes=0
        
        while redoTimes<3:
            try:
                #if it's the first time fetch uid from queue    
                if redoTimes==0:    
                    uid=self.candidateQueue.get(timeout=600)
                    self.deduplicator.add2Set('followRelation_uid',candidate)
                #get following list
                followList=spider.getfollow(uid)
                #put every uid into candidate Queue
                count=0
                for ele in followList:
                    # get uid of follow
                    candidate=ele['fid']
                    #if uid of follow has not been detected yet
                    if self.deduplicator.existInSet('uid',candidate)==False:
                        #added by 1
                        count+=1
                        #put it into to-be-visited queue
                        self.candidateQueue.put(candidate)
                        #put it to detected uid set(including visited and to be visited uid)
                        self.deduplicator.add2Set('uid',candidate)
                        #add it to stored list
                        obj=FollowRelation()
                        obj.inflate(ele)
                        self.storedList.append(obj)
                #when finished, set redoTimes=0
                redoTimes=0
                #logging
                logging.info('spider : '+username+' detected '+str(count)+' new user ids')
            #redo if it's HTTPError
            except urllib2.HTTPError as e:
                if redoTimes>3:
                    redoTimes=0
                    logging.warning(str(e))
                    logging.warning('spider '+username+' try more than 3 times, now give up collecting user : '+uid)
                else:
                    redoTimes+=1
                continue

            except BlockedException as e:
                #if there exsits other spider use it if run out of account , put remaining  data into file
                logging.error('username : '+username+' Blocked by Sina')
                if self.accounts.empty() == False:
                    m=self.accounts.get()
                    username=m['username']
                    password=m['password']
                    spider=FollowSpider(username,password)
                    continue
                else:
                    raise BlockedException('all spiders are used up')


            except urllib2.URLError as e:
                #network error, store data
                
                #step 1 : push data to somewhere
                self.storage.store2Object('FollowRelation',self.storedList)    
                self.storage.storeUID(self.storeList)
                #step 2 : pickling state
                self.candidateQueue.put(uid)
                self.storage.hiberCandidateQueue('FollowSpider_'+username,self.candidateQueue)
                logging.error(str(e))                
                logging.error('Network Error! Candidata Queue has been hibernated ')
                exit()
            
            except Queue.Empty as e:
                logging.info('All data in Queue is used up')
                #put all remaining list to file
                self.storage.store2Object('FollowRelation',self.storedList)
                self.storage.storeUID(self.storedList)
                exit()

            #when size of list arrives STORESIZE put them to file    
            if len(self.storedList) > self.STORESIZE:
                #put all uids into file
                self.storage.store2Object('FollowRelation',self.storedList)
                self.storage.storeUID(self.storedList)
                #clear store list
                self.storedList=[]


    def collectWeibo(self,username,password):
        #every spider is equiped with an account
        spider=WeiboSpider(username,password)
        self.deduplicator.setup('wid')
        #if HTTPError occurs only redo 3 times
        redoTimes=0
        
        while redoTimes<3:
            try:
                #if it's the first time fetch uid from queue    
                if redoTimes==0:    
                    uid=self.candidateQueue.get(timeout=600)
                    self.deduplicator.add2Set('weibo_uid',uid)
                #get following list
                weiboList=spider.getWeibo(uid)
                #put every uid into candidate Queue
                count=0
                for ele in weiboList:
                    # get uid of follow
                    candidate=ele['wid']
                    #if uid of follow has not been detected yet
                    if self.deduplicator.existInSet('wid',candidate)==False:
                        #added by 1
                        count+=1
                        self.deduplicator.add2Set('wid',candidate)
                        #add it to stored list
                        obj=Weibo()
                        obj.inflate(ele)
                        self.storedList.append(obj)
                #when finished, set redoTimes=0
                redoTimes=0
                #logging
                logging.info('spider : '+username+' detected '+str(count)+' new user weibos')
            #redo if it's HTTPError
            except urllib2.HTTPError as e:
                if redoTimes>3:
                    redoTimes=0
                    logging.warning(str(e))
                    logging.warning('spider '+username+' try more than 3 times, now give up collecting user : '+uid)
                else:
                    redoTimes+=1
                continue

            except BlockedException as e:
                #if there exsits other spider use it if run out of account , put remaining  data into file
                logging.error('username : '+username+' Blocked by Sina')
                if self.accounts.empty() == False:
                    m=self.accounts.get()
                    username=m['username']
                    password=m['password']
                    spider=WeiboSpider(username,password)
                    continue
                else:
                    raise BlockedException('all spiders are used up')


            except urllib2.URLError as e:
                #network error, store data
                
                #step 1 : push data to somewhere
                self.storage.store2Object('Weibo',self.storedList)    
                self.storage.storeUWID(self.storeList)
                #step 2 : pickling state
                self.candidateQueue.put(uid)
                self.storage.hiberCandidateQueue('Weibo_'+username,self.candidateQueue)
                logging.error(str(e))                
                logging.error('Network Error! Candidata Queue has been hibernated ')
                exit()
            
            except Queue.Empty as e:
                logging.info('All data in Queue is used up')
                #put all remaining list to file
                self.storage.store2Object('Weibo',self.storedList)
                self.storage.storeUWID(self.storedList)
                exit()

            #when size of list arrives STORESIZE put them to file    
            if len(self.storedList) > self.STORESIZE:
                #put all uids into file
                self.storage.store2Object('Weibo',self.storedList)
                self.storage.storeUWID(self.storedList)
                #clear store list
                self.storedList=[]




    def collectProfile(self,username,password):
        #every spider is equiped with an account
        spider=ProfileSpider(username,password)
        self.deduplicator.setup('profile_uid')
        #if HTTPError occurs only redo 3 times
        redoTimes=0
        
        while redoTimes<3:
            try:
                #if it's the first time fetch uid from queue    
                if redoTimes==0:    
                    uid=self.candidateQueue.get(timeout=600)
                #get profile of the uid
                profileList=spider.getProfile(uid)
                #put every uid into candidate Queue
                count=0
                for ele in profileList:
                    # get uid of user
                    candidate=ele['uid']
                    #if uid of follow has not been detected yet
                    if self.deduplicator.existInSet('profile_uid',candidate)==False:
                        #added by 1
                        count+=1
                        #put it to detected uid set
                        self.deduplicator.add2Set('profile_uid',candidate)
                        #add it to stored list
                        obj=Profile()
                        obj.inflate(ele)
                        self.storedList.append(obj)
                #when finished, set redoTimes=0
                redoTimes=0
                #logging
                logging.info('spider : '+username+' detected '+str(count)+' new user profile')
            #redo if it's HTTPError
            except urllib2.HTTPError as e:
                if redoTimes>3:
                    redoTimes=0
                    logging.warning(str(e))
                    logging.warning('spider '+username+' try more than 3 times, now give up collecting user : '+uid)
                else:
                    redoTimes+=1
                continue

            except BlockedException as e:
                #if there exsits other spider use it if run out of account , put remaining  data into file
                logging.error('username : '+username+' Blocked by Sina')
                if self.accounts.empty() == False:
                    m=self.accounts.get()
                    username=m['username']
                    password=m['password']
                    spider=ProfileSpider(username,password)
                    continue
                else:
                    raise BlockedException('all spiders are used up')


            except urllib2.URLError as e:
                #network error, store data
                
                #step 1 : push data to somewhere
                self.storage.store2Object('Profile',self.storedList)    
                #step 2 : pickling state
                self.candidateQueue.put(uid)
                self.storage.hiberCandidateQueue('ProfileSpider_'+username,self.candidateQueue)
                logging.error(str(e))                
                logging.error('Network Error! Candidata Queue has been hibernated ')
                exit()
            
            except Queue.Empty as e:
                logging.info('All data in Queue is used up')
                #put all remaining list to file
                self.storage.store2Object('Profile',self.storedList)
                exit()

            #when size of list arrives STORESIZE put them to file    
            if len(self.storedList) > self.STORESIZE:
                #put all uids into file
                self.storage.store2Object('Profile',self.storedList)
                #clear store list
                self.storedList=[]
    
                
    def collectComment(self,username,password):
        #every spider is equiped with an account
        spider=CommentSpider(username,password)
        self.deduplicator.setup('cid')
        #if HTTPError occurs only redo 3 times
        redoTimes=0
        
        while redoTimes<3:
            try:
                #if it's the first time fetch uid from queue    
                if redoTimes==0:    
                    uwid=self.candidateQueue.get(timeout=600)
                    self.deduplicator.add2Set('comment_uwid',uwid[0]+','+uwid[1])
                    print uwid
                    uid=uwid[0]
                    wid=uwid[1]
                #get comment of the uid
                commentList=spider.getComment(uid,wid)
                #put every uid into candidate Queue
                count=0
                for ele in commentList:
                    # get uid of user
                    candidate=ele['cid']
                    #if uid of follow has not been detected yet
                    if self.deduplicator.existInSet('cid',candidate)==False:
                        #added by 1
                        count+=1
                        #put it to detected cid set
                        self.deduplicator.add2Set('cid',candidate)
                        #add it to stored list
                        obj=Comment()
                        obj.inflate(ele)
                        self.storedList.append(obj)
                #when finished, set redoTimes=0
                redoTimes=0
                #logging
                logging.info('spider : '+username+' detected '+str(count)+' new user comment')
            #redo if it's HTTPError
            except urllib2.HTTPError as e:
                if redoTimes>3:
                    redoTimes=0
                    logging.warning(str(e))
                    logging.warning('spider '+username+' try more than 3 times, now give up collecting user : '+uid)
                else:
                    redoTimes+=1
                continue

            except BlockedException as e:
                #if there exsits other spider use it if run out of account , put remaining  data into file
                logging.error('username : '+username+' Blocked by Sina')
                if self.accounts.empty() == False:
                    m=self.accounts.get()
                    username=m['username']
                    password=m['password']
                    spider=CommentSpider(username,password)
                    continue
                else:
                    raise BlockedException('all spiders are used up')


            except urllib2.URLError as e:
                #network error, store data
                
                #step 1 : push data to somewhere
                self.storage.store2Object('Comment',self.storedList)    
                #step 2 : pickling state
                self.candidateQueue.put(uid)
                self.storage.hiberCandidateQueue('CommentSpider_'+username,self.candidateQueue)
                logging.error(str(e))                
                logging.error('Network Error! Candidata Queue has been hibernated ')
                exit()
            
            except Queue.Empty as e:
                logging.info('All data in Queue is used up')
                #put all remaining list to file
                self.storage.store2Object('Comment',self.storedList)
                exit()

            #when size of list arrives STORESIZE put them to file    
            if len(self.storedList) > self.STORESIZE:
                #put all uids into file
                self.storage.store2Object('Comment',self.storedList)
                #clear store list
                self.storedList=[]


if __name__ == '__main__':
    
    d=dispatcher()
    d.dispatch('Comment')
