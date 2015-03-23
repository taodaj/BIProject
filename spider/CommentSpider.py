#!/bin/python
# -*- coding: utf-8 -*-


import logging
import sys
import socket

from lxml import etree
import re
import pyquery
import time,datetime
import HTMLParser

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from Spider import *






class CommentSpider(Spider):

    def __init__(self,username,password):
        Spider.__init__(self,username,password)

    # get weibo comment
    def getComment(self, userid,weiboid):
        #list to store the people he follows
        self.userid=userid
        self.weiboid=weiboid
        commentList = []

        preURL = 'http://weibo.cn/'
        postURL = 'comment/'+weiboid + '?uid=' + userid + '&rl=2&page=1'
        expectedURLSeg='comment/'+weiboid + '?uid=' + userid

        while True:
            #HTTPError AND TIMEOUT , BlockedException may arise
            content=self.downloadHTML(preURL+postURL,expectedURLSeg)
            #extract data
            tree=etree.HTML(content)
            commentList.extend(self.extractComment(tree))
            #extract next url
            postURL=self.extractFollowUrl(content)
            if postURL == None:
                break

        return commentList



    def extractFollowUrl(self,content):
        html=pyquery.PyQuery(content)
        for ele in html('form a'):
            if pyquery.PyQuery(ele).text()==u'下页':
                return pyquery.PyQuery(ele).attr('href')
        return None


    def extractComment(self, tree):
        commentList = []
        idList = tree.xpath('//div/@id')

        for cid in idList:
            if(re.match('C_',cid)):
                xpath_comment='//div[@id="'+cid+'"]'+'/span[@class="ctt"]'
                xpath_comment_text='//div[@id="'+cid+'"]'+'/span[@class="ctt"]/text()'
                xpath_comment_at = '//div[@id="'+cid+'"]'+'/span[@class="ctt"]/a/text()'
                xpath_time='//div[@id="'+cid+'"]'+'/span[@class="ct"]/text()'
                xpath_agree='//div[@id="'+cid+'"]'+'/span[@class="cc"][1]/a/text()'
                #comment 评论内容
                comment = str(tree.xpath('string('+xpath_comment+')'))
                #agree 赞同数
                agree=str(tree.xpath(xpath_agree)[0][2])
                timearray=tree.xpath(xpath_time)[0].encode('utf-8').split('来自')[0].split(' ')

                time_sent = str(self.timeFormat(timearray))

                #print type(self.userid),type(self.weiboid),type(comment),type(agree),type(time_sent),type(cid)
                commentContent = {'uid':self.userid,'wid':self.weiboid,'comment':comment,'agree':agree,'time':time_sent,'cid':str(cid)}
                commentList.append(commentContent)

        return commentList

    #统一时间格式
    def timeFormat(self,timearray):

        if(len(timearray)==2):
            #eg 今天 21:59
            if(timearray[0]=="今天"):
                date_weibo = time.strftime('%Y-%m-%d',time.localtime(time.time()))
                time_weibo = timearray[1]
            #eg 2014-12-31 13:38:16
            elif(timearray[0].find('-') >= 0):
                time_hour = timearray[1].split(':')[0]
                time_min = timearray[1].split(':')[1]
                date_weibo = timearray[0]
                time_weibo = time_hour+':'+time_min

            #eg  01月02日 01:37
            elif(timearray[0].find('月') >= 0):
                time_month = timearray[0].split('月')[0]
                time_day = timearray[0].split('月')[1].split('日')[0]
                time_year = time.strftime('%Y',time.localtime(time.time()))
                time_weibo = timearray[1]
                date_weibo = time_year+'-'+time_month+'-'+time_day

            time_sent = date_weibo+' '+time_weibo
        #eg 1分钟前
        elif(len(timearray)==1):
            minute_ago = int(timearray[0].split('分钟前')[0])
            date_now = datetime.datetime.fromtimestamp(time.time())
            date_time_sent = date_now - datetime.timedelta(minutes=minute_ago)
            time_sent = datetime.datetime.strftime(date_time_sent,'%Y-%m-%d %H:%M')
        return unicode(time_sent,'utf8')

