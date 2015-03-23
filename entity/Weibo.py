#!/bin/python
# -*- coding: utf-8 -*-
from Entity import *
class Weibo(Entity):
    def __init__(self):
        self.wid='null'
        self.uid='null'
        self.content='null'
        self.time_sent='null'
        self.fowardingNum='null'
        self.commentNum='null'
        self.likeNum='null'
        self.plantform='null'
        self.fowardingWeiboId='null'
        self.atsList='null'
        #print "new Weibo"

    #def inflate(self,data):
    #    fields=data.split(',')
     #   self.wid=fields[0]
      #  self.uid=fields[1]
      #  self.content=fields[2]
     #   self.time_sent=fields[3]
    #    self.fowardingNum=fields[4]
     #   self.commentNum=fields[5]
      #  self.likeNum=fields[6]
      #  self.plantform=fields[7]
     #   self.fowardingWeiboId=fields[8]
    #   self.atsList=fields[9]

