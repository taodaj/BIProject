#!/usr/bin/python
# FileName : commentsInfo.py
# -*- coding:UTF-8 -*-

import sys
import userInfo.py
import weiboInfo.py

reload(sys)
sys.setdefaultencoding( "utf-8" )

class commentsInfo(object):
    def __init__(self,weiboid,userid,content,time,likeNum):
        self.weiboid=weiboid
        self.userid=userid
	self.content=content
	self.time=time
	self.fowardingNum=fowardingNum
	self.commentNum=commentNum
	self.likeNum=likeNum
	self.plantform=plantform
    def getWeiboid():
	return self.weiboid
    def getUserid():
	return self.userid
    def getContent():
	return self.content
    def getTime():
	return self.time
    def getLikeNum():
	return self.likeNum
    def setAT(object):
	self.atJson=atJson
    def getAT():
	return self.atJson
    

