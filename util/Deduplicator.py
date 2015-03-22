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





if __name__ == '__main__':
    pass
