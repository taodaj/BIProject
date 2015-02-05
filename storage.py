#!/usr/bin/python
# -*- coding:UTF-8 -*-

import pickle
import os
import Queue
import time


class storage:
    def __init__(self):
        #init
        pass

 
    #prefix is the prefix of a filename, storedList is the data to be stored
    def store2File(self,prefix,storedList):
        if os.path.exists('textData'+os.sep+prefix)==False:
            os.makedirs('textdata'+os.sep+prefix)
        f=open(os.getcwd()+os.sep+'textdata'+os.sep+prefix+os.sep+prefix+time.strftime('%Y_%m_%d_%H_%M_%S'),'w')
        for ele in storedList:
            f.write(ele+'\n')
        f.close()

    def store2Object(self,prefix,entityList):
        if os.path.exists('entityData'+os.sep+prefix)==False:
            os.makedirs('entityData'+os.sep+prefix)
        of=open(os.getcwd()+os.sep+'entityData'+os.sep+prefix+os.sep+prefix+time.strftime('%Y_%m_%d_%H_%M_%S'),'wb')
        pickle.dump(entityList,of)
        of.close()
        pass

    def store2DB(self):
        pass

    def hiberCandidateQueue(self,prefix,queue):
        #transform queue to list
        candidatelist=[]
        while queue.empty()==False:
            candidatelist.append(queue.get())
        if os.path.exists('hiber')==False:
            os.mkdir('hiber')
        of=open(os.getcwd()+os.sep+'hiber'+os.sep+prefix+'_'+time.strftime('%Y_%m_%d_%H_%M_%S'),'wb')
        pickle.dump(candidatelist,of)
        of.close()

    def storeUID(self,eles):
        if os.path.exists('ids')==False:
            os.mkdir('ids')
        of=open(os.getcwd()+os.sep+'ids'+os.sep+'uid_'+time.strftime('%Y_%m_%d_%H_%M_%S'),'w')
        for ele in eles:
            of.write(ele.fid+'\n')
        of.close()

    def storeUWID(self,eles):
        if os.path.exists('ids')==False:
            os.mkdir('ids')
        of=open(os.getcwd()+os.sep+'ids'+os.sep+'uwid_'+time.strftime('%Y_%m_%d_%H_%M_%S'),'w')
        for ele in eles:
            of.write(ele.uid+','+ele.wid+'\n')
        of.close()  



if __name__ == '__main__':
    s=storage()
    q=Queue.Queue()
    q.put(1)
    s.hiberCandidateQueue(q)
