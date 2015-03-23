#!/bin/python
#coding: utf-8

import Queue
import urllib2
import sys
import logging
import pickle
import os
import threading
import time
import signal

from spider import *
from entity import *
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

 
    def __init__(self,spiderType,num_of_threads):
        logging.debug('get into __init__()')
        #MODIFY HERE!!!!!
        self.STORESIZE=100
        self.spiderType=spiderType
        self.num_of_threads=num_of_threads
        self.accounts=Queue.Queue()        
        #work queue which spiders fetch id from
        self.workQueue=Queue.Queue()
        #result Queue which spiders put data
        self.resultQueue=Queue.Queue()
        # storage Class
        self.storage=storage()
        #deduplicator Class
        self.deduplicator=util.Deduplicator()
        # 
        self.event=threading.Event()
        self.threads=[]



        self.initAccount()
        self.prepareSource()
        self.initThread()


    def prepareSource(self):
        logging.debug('get into prepareSource()')

        if self.spiderType=='FollowRelation':
            source=self.deduplicator.diffSet('uid','follow_uid_visited')
        elif self.spiderType=='Profile':
            source=self.deduplicator.diffSet('uid','profile_uid_visited')

        elif self.spiderType=='Weibo':
            source=self.deduplicator.diffSet('uid','weibo_uid_visited')

        elif self.spiderType=='Comment':       
            source=self.deduplicator.diffSet('uwid','comment_uwid_visited')

        count=0
        for ele in source:
            if(count==100):
                break
            self.workQueue.put(ele)

    def initThread(self):
        logging.debug('get into initThread()')
        
        try:   
            if self.spiderType=='FollowRelation':
                for i in range(self.num_of_threads):
                    ac=self.accounts.get(False)
<<<<<<< HEAD
                    thread=FollowSpider(ac['username'],ac['password'],self.deduplicator,self.workQueue,self.resultQueue,self.event)
=======
                    thread=FollowWorker(ac['username'],ac['password'],self.deduplicator,self.workQueue,self.resultQueue,self.event)
>>>>>>> origin
                    self.threads.append(thread)
            elif self.spiderType=='Profile':
                for i in range(self.num_of_threads):
                    ac=self.accounts.get(False)
<<<<<<< HEAD
                    thread=ProfileSpider(ac['username'],ac['password'],self.deduplicator,self.workQueue,self.resultQueue,self.event)
=======
                    thread=ProfileWorker(ac['username'],ac['password'],self.deduplicator,self.workQueue,self.resultQueue,self.event)
>>>>>>> origin
                    self.threads.append(thread)
            elif self.spiderType=='Weibo':
                for i in range(self.num_of_threads):
                    ac=self.accounts.get(False)
<<<<<<< HEAD
                    thread=WeiboSpider(ac['username'],ac['password'],self.deduplicator,self.workQueue,self.resultQueue,self.event)
=======
                    thread=WeiboWorker(ac['username'],ac['password'],self.deduplicator,self.workQueue,self.resultQueue,self.event)
>>>>>>> origin
                    self.threads.append(thread)
            elif self.spiderType=='Comment':
                for i in range(self.num_of_threads):
                    ac=self.accounts.get(False)
<<<<<<< HEAD
                    thread=CommentSpider(ac['username'],ac['password'],self.deduplicator,self.workQueue,self.resultQueue,self.event)
=======
                    thread=CommentWorker(ac['username'],ac['password'],self.deduplicator,self.workQueue,self.resultQueue,self.event)
>>>>>>> origin
                    self.threads.append(thread)

            
        except Queue.Empty as e:
            logging.info('Accounts used up During init stage, '+str(len(self.threads))+' threads start')

    def dispatch(self):
        logging.debug('get into dispatch()')

        for thread in self.threads:
            thread.start()


        while True:
            #check whether spider is blocked
            for i in range(len(self.threads)):
                if self.threads[i].status=='blocked':
                    del self.threads[i]
                    self.addWorker()

            #check whether workQueue is empty
            if self.event.isSet()==False:
                self.prepareSource()
                self.event.set()

            #check whether the size of resultQueue reaches self.STORESIZE
            if self.resultQueue.qsize()>self.STORESIZE:
                logging.info('Size of result queue reaches '+str(self.resultQueue.qsize()))
                try:
                    self.storeData()
                except Queue.Empty as e:
                    pass
            # check every 30s
<<<<<<< HEAD
            time.sleep(30)
=======
            time.sleep(5)
>>>>>>> origin



    def storeData(self):
        logging.debug('get into storeData()')
        storedList=[]
        for i in range(self.STORESIZE):
            storedList.append(self.resultQueue.get(False))

        self.storage.store2Object(self.spiderType,storedList)        



    def addWorker(self):
        logging.debug('get into addWorker()')
        
        try:
            ac=self.accounts.get(False)   
            if self.spiderType=='FollowRelation':  

<<<<<<< HEAD
                thread=FollowSpider(ac['username'],ac['password'],self.deduplicator,self.workQueue,self.resultQueue,self.event)

            elif self.spiderType=='Profile':

                thread=ProfileSpider(ac['username'],ac['password'],self.deduplicator,self.workQueue,self.resultQueue,self.event)

            elif self.spiderType=='Weibo':

                thread=WeiboSpider(ac['username'],ac['password'],self.deduplicator,self.workQueue,self.resultQueue,self.event)

            elif self.spiderType=='Comment':

                thread=CommentSpider(ac['username'],ac['password'],self.deduplicator,self.workQueue,self.resultQueue,self.event)
=======
                thread=FollowWorker(ac['username'],ac['password'],self.deduplicator,self.workQueue,self.resultQueue,self.event)

            elif self.spiderType=='Profile':

                thread=ProfileWorker(ac['username'],ac['password'],self.deduplicator,self.workQueue,self.resultQueue,self.event)

            elif self.spiderType=='Weibo':

                thread=WeiboWorker(ac['username'],ac['password'],self.deduplicator,self.workQueue,self.resultQueue,self.event)

            elif self.spiderType=='Comment':

                thread=CommentWorker(ac['username'],ac['password'],self.deduplicator,self.workQueue,self.resultQueue,self.event)
>>>>>>> origin

            self.threads.append(thread)
            thread.start()

            
        except Queue.Empty as e:
            logging.info('Accounts used up, Now exists'+str(len(self.threads))+' threads')       




    def initAccount(self,source='ids/accounts'):
        logging.debug('get into initAccount()')

        f=open(source,'r')
        for line in f:
            line=line[:-1].split(' ')
            m={}
            m['username']=line[0]
            m['password']=line[1]
            self.accounts.put(m)
        f.close()

    #only works when waiting for source
    def signal_handler(self,signal, frame):
        #stop thread in threads
        logging.debug('get into signal_handler()')
        for thread in self.threads:
            thread.stop()
        self.event.set()
        
        #wait till all threads terminate
        singal=False
        while True:
            for thread in self.threads:
                if thread.isAlive():
                    break
                singal=True

            if singal:
                break      
            time.sleep(1)

        try:
            while True:
                self.storeData()
        except Queue.Empty as e:
            pass

        logging.info('program exit')
        sys.exit(0)


if __name__ == '__main__':

    
<<<<<<< HEAD
    d=dispatcher('Comment',2)
=======
    d=dispatcher('FollowRelation',2)
>>>>>>> origin
    signal.signal(signal.SIGINT, d.signal_handler)
    d.dispatch()

