#!/usr/bin/python
# -*- coding:UTF-8 -*-

import redis

class InvalidSetNameException(Exception):
    def __init__(self,*args):
        Exception.__init__(self,*args)

class Deduplicator:
    #init, connect to redis
    def __init__(self,host='127.0.0.1',port=6379,db=0):
        self.redis_db=redis.StrictRedis(host,port,db)

    def setup(self,setName):
        #init
        self.redis_db.sadd(setName,'none')
    
    
    def existInSet(self,setName,item):
        if self.redis_db.sismember(setName,item) == 1:
            return True
        else:
            return False


    def add2Set(self,setName,item):
        self.redis_db.sadd(setName,item)

    def sortSet(self,setName):
        pass


    def delSet(self,setName):
        self.redis_db.delete(setName)

    def diffSet(self,setNameA,setNamaB):
        return self.redis_db.sdiff(setNameA,setNamaB)

    #用来记录对应用户(uid)的最新微博(wid),与对应微博(wid)的最新评论(cid)
    #eg. self.deduplicator.hashSet('latest_weibo',uid,wid)
    #eg. self.deduplicator.hashSet('latest_comment',wid,cid)
    def hashSet(self,setName,field,value):
        self.redis_db.hset(setName,field,value)

    #用来得到对应用户(uid)的最新微博(wid),与对应微博(wid)的最新评论(cid)
    #eg. self.deduplicator.hashGet('latest_weibo',uid)
    #eg. self.deduplicator.hashGet('latest_comment',wid)    
    def hashGet(self,setName,field):
        return self.redis_db.hget(setName,field)





if __name__ == '__main__':
    pass
