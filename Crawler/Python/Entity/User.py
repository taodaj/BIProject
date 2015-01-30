#!/bin/python
# -*- coding: utf-8 -*-

class User:
    def __init__(self):
        print "new User"

    def inflate(self,data):
        fields=data.split(',')
        self.uid=fields[0]
        self.fuid=fields[1]

