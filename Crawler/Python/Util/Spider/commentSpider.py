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
from lxml import etree
import spider as Spider
import re
import datetime
import HTMLParser
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
reload(sys)
sys.setdefaultencoding('utf-8')

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    stream=sys.stdout
                    )




class commentSpider(Spider.spider):
    def __init__(self,username,password):
        Spider.spider.__init__(self,username,password)

    # get the users he follows
    def getComment(self, userid,weiboid):
        #list to store the people he follows
        self.userid=userid
        self.weiboid=weiboid
        commentList = []
        url_base='http://weibo.cn/comment/' + weiboid + '?uid=' + userid + '&rl=2&page='
        url = url_base+'1'

        expectedURLSeg='weibo.cn/comment/'+weiboid + '?uid=' + userid

        try:
            #HTTPError AND TIMEOUT , BlockedException may arise
            content=self.downloadHTML(url,expectedURLSeg)
            #extract data
            self.content=content


        except socket.timeout as e:
                #logging
            logging.warning('TIME OUT, try again from '+url)


        # get page num
        tree=etree.HTML(self.content)
        commentList.extend(self.extractComment(tree))

        pageNum=0
        try:
            pageNum = tree.xpath('id("pagelist")/form/div/text()[2]')[0]
        except:
            logging.warning('TIME OUT, try again from '+url)
        pageNum = pageNum.encode('utf-8')
        index = pageNum.find('页')-1
        pageNum = pageNum[index]

        for i in range(2,int(pageNum)+1):
            print i,'page'
            url = url_base+str(i)
            try:
                content=self.downloadHTML(url,'weibo.cn/comment/')
                self.content=content
            except:
                logging.warning('TIME OUT, try again from '+url)
            tree=etree.HTML(self.content)
            commentList.extend(self.extractComment(tree))


        return commentList


    def extractComment(self, tree):
        commentList = []
        idList = tree.xpath('//div/@id')
        for id in idList:
            if(re.match('C_',id)):
                xpath_comment='//div[@id="'+id+'"]'+'/span[@class="ctt"]'
                xpath_comment_text='//div[@id="'+id+'"]'+'/span[@class="ctt"]/text()'
                xpath_comment_at = '//div[@id="'+id+'"]'+'/span[@class="ctt"]/a/text()'
                xpath_time='//div[@id="'+id+'"]'+'/span[@class="ct"]/text()'
                xpath_agree='//div[@id="'+id+'"]'+'/span[@class="cc"][1]/a/text()'
                comment = tree.xpath(xpath_comment)[0]
                comment_text = tree.xpath(xpath_comment_text)
                comment_at = tree.xpath(xpath_comment_at)
                agree=tree.xpath(xpath_agree)[0][2]
                timearray=tree.xpath(xpath_time)[0].encode('utf-8').split('来自')[0].split(' ')
                if(len(timearray)==2):
                    if(timearray[0]=="今天"):
                        timearray[0] = time.strftime('%m月%d日',time.localtime(time.time()))
                    time_sent = timearray[0]+' '+timearray[1]
                elif(len(timearray)==1):
                    minute_ago = int(timearray[0].split('分钟前')[0])
                    minute_now = int(time.strftime('%M',time.localtime(time.time())))
                    date_minute_now = datetime.datetime.fromtimestamp(minute_now)
                    date_time_sent = date_minute_now - datetime.timedelta(minutes=minute_ago)
                    print date_time_sent
                    time_sent = datetime.datetime.strftime(date_time_sent,'%m月%d日 %H时%M分')

                #comment
                if len(comment_at)==0 :
                    comment=comment_text[0]
                elif len(comment_text)==0:
                    comment=comment_at[0]
                else:
                    comment=ET.tostring(comment)
                    comment = comment.replace('<span class="ctt">','')
                    comment = comment.replace('</a>:','')
                    comment = comment.replace('</span>    &#160;','')
                    reobj = re.compile('<a[^>]*>')
                    comment = reobj.subn('', comment)[0]
                    comment = HTMLParser.HTMLParser().unescape(comment)

                print agree,time_sent,comment
                commentList.append(self.userid+','+self.weiboid+','+comment+','+agree+','+unicode(time_sent,'utf8'))

        return commentList

if __name__ == '__main__':
    #!!!!USE YOUR USERNAME AND PASSWORD HERE
    Spider.spider = commentSpider('18612986170', '18612986170')
    print Spider.spider.getComment('1644088832','C1JhOhrwM')
