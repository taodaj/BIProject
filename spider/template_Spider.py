#!/bin/python
# -*- coding: utf-8 -*-

import cookielib
import urllib
import urllib2
import pyquery
import logging
import time
import random
import sys
import socket
from spider import spider
from spider import BlockedException

logging.basicConfig(level=logging.DEBUG,  
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',  
                    datefmt='%a, %d %b %Y %H:%M:%S',  
                    stream=sys.stdout  
                    ) 



#这里换成自己对应的爬虫名字
class followSpider(spider):
    def __init__(self,username,password):
        spider.__init__(self,username,password)        

    #这里实现自己提取出对应信息的方法(方法名自己取哦)
    #注意事项：
    #1.要能够翻页(翻页的URL如果能从href里面拿到，尽量从href拿)
    #2.有时间这个属性的要对时间格式进行处理(会封装成一个函数)
    #3.
    #函数头参考：
    #getProfile(self,uid)
    #getWeibo(self,uid)
    #getComment(self,uid,wid)
    def getfollow(self,userid):
        #用这个方法得到对应的网网页
        #不用再处理socket.timeout错误了，已经在内部处理了
        #可能抛出HTTPEEOR,URLEEROR,不需要在此捕获      
        content=self.downloadHTML(URL,expectedURLSeg)
        #然后对对应的网页做提取
        
        
        #返回类型是一个 dict 的 list
        #dict 里面是对应Entity里面的属性名与提取出来的值(务必保证这边的key和Entity里面的属性名相同)
        #例如: obj['uid']=123456
        return followList

    
if __name__ == '__main__':
    #!!!!USE YOUR USERNAME AND PASSWORD HERE
    spider = followSpider(USERNAME, PASSWORD)
    print spider.getfollow('3399558022')
