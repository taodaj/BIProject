#import sys
#import os
#sys.path.append(os.path.abspath('..'))

from Spider import * 
from CommentSpider import CommentSpider
from entity import *

from urllib2 import *
import threading
import Queue

class CommentWorker(threading.Thread):
    def __init__(self,username,password,deduplicator,workQueue,resultQueue,event):     
        threading.Thread.__init__(self)
        self.name=username
        self.deduplicator=deduplicator
        self.workQueue=workQueue
        self.resultQueue=resultQueue
        self.event=event
        self.spider=CommentSpider(username,password)
        self.status='normal'

    def run(self):
    #if HTTPError occurs only redo 3 times
        logging.debug(self.name + ' gets into run()')
        redoTimes=0
        
        while redoTimes<3:
            try:
                #if it's the first time, fetch uwid from queue    
                if redoTimes==0:    
                    uwid=self.workQueue.get(False).split(',')
                    self.deduplicator.add2Set('comment_uwid_visited',uwid[0]+','+uwid[1])

                #get comment list
                commentList=self.spider.getComment(uwid[0],uwid[1])

                count=0
                for ele in commentList:
                    # get wid of follow
                    candidate=ele['wid']+','+ele['cid']
                    #put all wcid detected into 'wcid' set
                    if self.deduplicator.existInSet('wcid',candidate)==False:
                        #added by 1
                        count+=1       
                        self.deduplicator.add2Set('wcid',candidate)
                        #add it to result queue
                        obj=Comment()
                        obj.inflate(ele)
                        self.resultQueue.put(obj)
                #when finished, set redoTimes=0
                redoTimes=0
                #logging
                logging.info('spider : '+self.name+' detected '+str(count)+' new comments')
            #redo if it's HTTPError
            except urllib2.HTTPError as e:
                if redoTimes>3:
                    redoTimes=0
                    logging.warning(str(e))
                    logging.warning('spider '+self.name+' try more than 3 times, give up collecting from wcid : '+candidate)
                else:
                    redoTimes+=1


            except BlockedException as e:
                logging.info('spider '+self.name+' is blocked by Sina')
                self.status='blocked'
                break

            except urllib2.URLError as e:
                #network error, no internet available
                raise e
            
            except Queue.Empty as e:
                self.event.clear()
                logging.info('spider : '+self.name+' waits for resource')
                self.event.wait()
                logging.info('spider : '+self.name+' restarts')

