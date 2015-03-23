#!/bin/python
# -*- coding: utf-8 -*-

from Entity import *

class FollowRelation(Entity):


    def __init__(self):
        Entity.__init__(self)
        self.uid='null'
        self.fid='null'


if __name__ == '__main__':
    f=FollowRelation()
    map={'uid':[1,2,3],'fid':1111}
    f.inflate(map)
    print f.uid
    print f.fid
