#!/bin/python
#fileName:dispatcher.py
# -*- coding: utf-8 -*-


import Queue
import urllib2
import sys
import logging
import pickle
sys.path.append('..')
import Util.Spider.followingSpider
from Util.Spider.spider import BlockedException
from Util.Process.storage import storage
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
    def __init__(self,candidateQueue):
        #candidate queue which spider fetches uid from
        self.candidateQueue=candidateQueue
        #list to keep  (names,uids,fans) detected 
        self.storedList=[]
        # storage Class
        self.storage=storage()

    def collectFollowing(self):
        #every spider is equiped with a account
        spider=followingSpider.followingSpider(USERNAME, PASSWORD)
        #if HTTPError occurs only redo 3 times
        redoTimes=0
        
        while self.candidateQueue.empty()==False or redoTimes>0:
            try:
                #if it's the first time fetch uid from queue    
                if redoTimes==0:    
                    uid=self.candidateQueue.get()
                #get following list
                followingList=spider.getfollowing(uid)
                #put every uid into candidate Queue
                for ele in followingList:
                    #split csv to get uid
                    candidate=ele.split(',')[1]
                    #if uid havent been detected yet
                    if self.storage.existInSet('uid',candidate)==False:
                        #put it into to-be-visited queue
                        self.candidateQueue.put(candidate)
                        #put it to detected uid set
                        self.storage.add2Set('uid',candidate)
                        #add it to stored list
                        self.storedList.append(ele)
                #when finished, set redoTimes=0
                redoTimes=0
                #logging
                logging.info('detected '+str(len(followingList))+' users')
            #redo if it's HTTPError
            except urllib2.HTTPError as e:
                if redoTimes>3:
                    redoTimes=0
                    logging.warning(str(e))
                    logging.warning('try more than 3 times give up collecting user : '+uid)
                else:
                    redoTimes+=1
                continue
            except BlockedException as e:
                #if there exsits other spider use it if run out of account , put remaining  data into file
                logging.error('Blocked by Sina')


                #####################################
                #### i am a cute unfinished mark ####
                #####################################

                raise e

            except urllib2.URLError as e:
                #network error, store data
                
                #step 1 : push data to somewhere
                self.storage.storeToFile(filename+str(count),self.storedList)    
                #step 2 : pickling state
                self.storage.hiberCandidateQueue(candidateQueue)
                logging.error(str(e))                
                logging.error('Network Error! Candidata Queue has been hibernated ')
                exit()

            #when size of list arrives 100 put them to file    
            if len(self.storedList) > 100:
                #put all uids into file
                self.storage.store2File(u'following',self.storedList)
                #clear store list
                self.storedList=[]
        #put all remaining list to file
        self.storage.store2File(u'following',self.storedList)
                


if __name__ == '__main__':
    queue=Queue.Queue()
    queue.put('1644088831')
    d=dispatcher(queue)
    d.collectFollowing()
