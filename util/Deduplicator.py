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
        self.validateSetName(setName)
        if self.redis_db.sismember(setName,item) == 1:
            return True
        else:
            return False


    def add2Set(self,setName,item):
        self.validateSetName(setName)
        self.redis_db.sadd(setName,item)

    def sortSet(self,setName):
        self.validateSetName(setName)
        pass

    def validateSetName(self,setName):
        if self.redis_db.sismember(setName,'none')==0:
            raise InvalidSetNameException('no "'+setName+'" is kept in db')

    def delSet(self,setName):
        self.redis_db.delete(setName)





if __name__ == '__main__':
    pass
