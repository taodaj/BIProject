#!/usr/bin/python
# FileName : weiboInfo.py
# -*- coding:UTF-8 -*-

import sys
import sys

sys.path.append('..')
import WeiboElement.userInfo

reload(sys)
sys.setdefaultencoding( "utf-8" )

class weiboInfo():

    def __init__(self,weiboid,userid,content,time,fowardingNum,commentNum,likeNum,plantform):
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
    def getFowardingNum():
        return self.fowardingNum
    def getCommentNum():
        return self.commentNum
    def getLikeNum():
        return self.likeNum
    def getPlantform():
        return self.plantform
    def setAT(self,object):
        self.atJson=object
    def getAT():
        return self.atJson
    def setfowardingWeiboId(self,object):
        self.fowardingWeiboId=object
    def getfowardingWeiboId():
        return self.fowardingWeiboId
print "asdkfjaksdf"
    
