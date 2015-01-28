#!/usr/bin/python
# FileName : relationInfo.py
# -*- coding:UTF-8 -*-

class relationInfo:
    #userid follow followingId
    def __init__(self,userId,followingId):
        self.userId=userId
	self.followingId=followingId
    def setUserId(self,userId):
        self.userId=userId
    def setFollowingId(self,followingId):
        self.followingId=followingId
    def getUserId(self):
        return self.userId
    def getFollowingId(self):
        return self.followingId

    

