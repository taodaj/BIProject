#!/usr/bin/python
# -*- coding:UTF-8 -*-

import redis
import pickle
import os
import Queue
import time

class InvalidSetNameException(Exception):
    def __init__(self):
        Exception.__init__(self)

class storage:
    def __init__(self,host='127.0.0.1',port=6379,db=0):
        self.redis_db=redis.StrictRedis(host,port,db)
        #init
        self.delSet()
        self.redis_db.sadd('uid','none')
        self.redis_db.sadd('wid','none')
        self.redis_db.sadd('cid','none')
    
    def existInSet(self,setName,uid):
        self.validateSetName(setName)
        if self.redis_db.sismember(setName,uid) == 1:
            return True
        else:
            return False


    def add2Set(self,setName,uid):
        self.validateSetName(setName)
        self.redis_db.sadd(setName,uid)

    def sortSet(self,setName):
        self.validateSetName(setName)
        pass

    def validateSetName(self,setName):
        if setName not in ('uid','wid','cid'):
            raise InvalidSetNameException()

    def delSet(self):
            self.redis_db.delete('uid')
            self.redis_db.delete('wid')
            self.redis_db.delete('cid')

    #prefix is the prefix of a filename, storedList is the data to be stored
    def store2File(self,prefix,storedList):
        if os.path.exists('textData')==False:
            os.mkdir('textdata')
        f=open(os.getcwd()+os.sep+'textdata'+os.sep+prefix+time.strftime('%Y_%m_%d_%H_%M_%S'),'w')
        for ele in storedList:
            f.write(ele+'\n')
        f.close()

    def store2Object(self,prefix,entityList):
        if os.path.exists('entityData')==False:
            os.mkdir('entityData')
        of=open(os.getcwd()+os.sep+'entityData'+os.sep+prefix+time.strftime('%Y_%m_%d_%H_%M_%S'),'wb')
        pickle.dump(entityList,of)
        of.close()
        pass

    def store2DB(self):
        pass

    def hiberCandidateQueue(self,queue):
        #transform queue to list
        candidatelist=[]
        while queue.empty()==False:
            candidatelist.append(queue.get())
        if os.path.exists('pickling')==False:
            os.mkdir('pickling')
        of=open(os.getcwd()+os.sep+'pickling'+os.sep+'cq_'+time.strftime('%Y_%m_%d_%H_%M_%S'),'wb')
        pickle.dump(candidatelist,of)
        of.close()
                    



if __name__ == '__main__':
    s=storage()
    q=Queue.Queue()
    q.put(1)
    s.hiberCandidateQueue(q)
