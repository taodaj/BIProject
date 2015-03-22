#import sys
#import os
#sys.path.append(os.path.abspath('..'))

from Spider import * 
from WeiboSpider import WeiboSpider
from entity import *

from urllib2 import *
import threading
import Queue

class WeiboWorker(threading.Thread):
    def __init__(self,username,password,deduplicator,workQueue,resultQueue,event):
        threading.Thread.__init__(self)
        self.name=username
        self.deduplicator=deduplicator
        self.workQueue=workQueue
        self.resultQueue=resultQueue
        self.event=event
        self.spider=WeiboSpider(username,password)
        self.status='normal'

    def run(self):
    #if HTTPError occurs only redo 3 times
        logging.debug(self.name + ' gets into run()')
        redoTimes=0
        
        while redoTimes<3:
            try:
                #if it's the first time fetch uid from queue    
                if redoTimes==0:    
                    uid=self.workQueue.get(False)
                    self.deduplicator.add2Set('weibo_uid_visited',uid)
                #get weibo list
                weiboList=self.spider.getWeibo(uid)
                count=0
                for ele in weiboList:
                    # get wuid 
                    candidate=ele['uid']+','+ele['wid']
                    #if this weibo hasnt been collected before
                    if self.deduplicator.existInSet('uwid',candidate)==False:
                        #added by 1
                        count+=1       
                        self.deduplicator.add2Set('uwid',candidate)
                        #add it to stored list
                        obj=Weibo()
                        obj.inflate(ele)
                        self.resultQueue.put(obj)
                #when finished, set redoTimes=0
                redoTimes=0
                #logging
                logging.info('spider : '+self.name+' detected '+str(count)+' new weibo')
            #redo if it's HTTPError
            except urllib2.HTTPError as e:
                if redoTimes>3:
                    redoTimes=0
                    logging.warning(str(e))
                    logging.warning('spider '+self.name+' try more than 3 times, now give up collecting weibo : '+candidate)
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

