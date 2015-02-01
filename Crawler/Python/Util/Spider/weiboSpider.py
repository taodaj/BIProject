#-*- coding: UTF-8 -*-
#!/usr/bin/python
#fileName:weiboSpider.py

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
import datetime
reload(sys)
sys.setdefaultencoding('utf-8')

logging.basicConfig(level=logging.DEBUG,  
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',  
                    datefmt='%a, %d %b %Y %H:%M:%S',  
                    stream=sys.stdout  
                    ) 
class weiboSpider(Spider.spider):
    def __init__(self,username,password):
        Spider.spider.__init__(self,username,password)
    
    #get the users' weibo
    def getWeibo(self,userid):
        #weibo list
        weiboList=[]
        content=''
        preURL='http://weibo.cn'
        postURL='/u/'+userid
        expectedURLSeg='weibo.cn/u/'+userid
        while True:
            try:
                #HTTPError AND TIMEOUT , BlockedException may arise
                content=self.downloadHTML(preURL+postURL,expectedURLSeg)
                #extract data
                weiboList.extend(self.extractFollowing(content,userid))
                #extract next url
                postURL=self.extractFollowingUrl(content)
                if postURL == None:
                    print 'Cant get postURL'
                    break
            except socket.timeout as e:
                #logging
                logging.warning('TIME OUT, try again from '+postURL)
                continue
        return weiboList
    
    def extractFollowingUrl(self,content):
        tree=etree.HTML(content)
        for ele in tree.xpath(u"//div[@class='pa' and @id='pagelist']"):
            if ele.xpath(u"form/div/a")[0].text==u'下页':
                return ele.xpath(u"form/div/a")[0].get("href")
        return None

    #ATTENTION: Here assume spider follows nobody
    def extractFollowing(self,contents,userid):
        pageList=[]
        tree=etree.HTML(contents)
        i=0
        for ele in tree.xpath(u"//div[@class='c' and @id]"):
            try:
                xpath_href = u"div/span[@class='cmt']/a"
                xpath_href_contentList=u"div[last()]/text()"
                xpath_contentList=u"div/span[@class='ctt']/text()"
                xpath_href_ats=u"div[last()]/a"
                xpath_ats=u"div/span[@class='ctt']/a"
                xpath_like=u"div[last()]/a[last()-3]"
                xpath_comment=u"div[last()]/a[last()-1]"
                xpath_fowarding=u"div[last()]/a[last()-2]"
                xpath_info=u"div[last()]/span[@class='ct']"
                weiboid=ele.get("id").split('_')[1]
                print weiboid
                hrefs = ele.xpath(xpath_href)
                fowardingWeiboId=""
                atsList=""
                content=""
                if hrefs:
                    fowardingWeiboId=hrefs[0].text
                    contentList=ele.xpath(xpath_contentList)
                    for contents in contentList:
                        content+=contents
                    ats=ele.xpath(xpath_href_ats)
                else :
                    contentList=ele.xpath(xpath_contentList)
                    for contents in contentList:
                        content+=contents
                    ats=ele.xpath(xpath_ats)
                for at in ats:
                    strat=at.get('href')
                    if strat.find('/n/')!=-1:
                        atsList+=at.text[1:]+"//"
                #print content
                likeNum=ele.xpath(xpath_like)[0].text
                commentNum=ele.xpath(xpath_comment)[0].text
                fowardingNum=ele.xpath(xpath_fowarding)[0].text
                info=ele.xpath(xpath_info)[0].text.split(u'来自')
                timearray=info[0].split(' ')
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
                plantform=info[1]
                if type(content) == type(None):
                    logging.warning('Did not get '+weiboid+'content ')
                    content= " "
                print time_sent
                pageList.append(weiboid+','+userid+','+content+','+time_sent+','+fowardingNum+','+commentNum +','+likeNum+','+plantform+','+fowardingWeiboId+','+atsList)
            except AttributeError as e:
                logging.warning(str(e))
                continue
        return pageList

if __name__ == '__main__':
    #!!!!USE YOUR USERNAME AND PASSWORD HERE
    Spider.spider = weiboSpider("18811442500", "742612")
    count=1     
    file = open("test-uids")
    while 1:
        line = file.readline()
        if not line:
            break
        pass # do something
        print count
        uid=line[0:10]
        print uid
        count=count+1
        Spider.spider.getWeibo(uid)