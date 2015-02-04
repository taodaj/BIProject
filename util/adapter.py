#!/bin/python
# -*- coding: utf-8 -*-

from Entity import *


#inflate entity using data, for each Entity, it should be equiped with an inflate() method 

def transList2FollowingRelation(datalist):
    entityList=[]
    for ele in datalist:
        fr=FollowingRelation()
        fr.inflate(ele)
        entityList.append(fr)
    return entityList

def transList2Comment(datalist):
    pass

def transList2User(datalist):
    pass

def transList2Weibo(datalist):
    pass

