#!/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append('../..')
print sys.path
from Entity import Comment
from Entity import FollowingRelation
import Entity.User as User
import Entity.Weibo as Weibo


#inflate entity using data, for each Entity, it should be equiped with an inflate() method 

def transList2FollowingRelation(datalist):
    entityList=[]
    for ele in datalist:
        fr=FollowingRelation()
        fr.inflate(ele)
        entityList.append(fr)
    return entityList

def transList2Comment(datalist):
    entityList=[]
    for ele in datalist:
        fr=Comment()
        fr.inflate(ele)
        entityList.append(fr)
    return entityList

def transList2User(datalist):
    entityList=[]
    for ele in datalist:
        fr=User()
        fr.inflate(ele)
        entityList.append(fr)
    return entityList

def transList2Weibo(datalist):
    entityList=[]
    for ele in datalist:
        fr=Weibo()
        fr.inflate(ele)
        entityList.append(fr)
    return entityList
if __name__ == '__main__':
    print transList2FollowingRelation(["1,2"])

