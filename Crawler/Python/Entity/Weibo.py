#!/bin/python
# -*- coding: utf-8 -*-

class Weibo:
    def __init__(self):
        print "new Weibo"

    def inflate(self,data):
        fields=data.split(',')
        self.weiboid=fields[0]
        self.userid=fields[1]
        self.content=fields[2]
        self.time=fields[3]
        self.fowardingNum=fields[4]
        self.commentNum=fields[5]
        self.likeNum=fields[6]
        self.plantform=fields[7]
        self.fowardingWeiboId=fields[8]
        self.atJson=fields[9]

