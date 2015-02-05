#!/bin/python
# -*- coding: utf-8 -*-

from Entity import *

class Comment(Entity):
    def __init__(self):
        Entity.__init__(self)
        #init your attr
        #eg self.uid='null'
        self.userid='null'
        self.weiboid='null'
        self.comment='null'
        self.agree='null'
        self.time='null'
        

