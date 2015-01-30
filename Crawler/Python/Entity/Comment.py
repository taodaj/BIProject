#!/bin/python
#fileName:Comment.py
# -*- coding: utf-8 -*-
class Comment:
    def __init__(self):
        print "new Comment"

    def inflate(self,data):
        fields=data.split(',')
        self.userid=fields[0]
        self.weiboid=fields[1]
        self.content=fields[2]
        self.likeNum=fields[3]
        self.time=fields[4]
