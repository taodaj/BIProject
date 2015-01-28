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

logging.basicConfig(level=logging.DEBUG,  
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',  
                    datefmt='%a, %d %b %Y %H:%M:%S',  
                    stream=sys.stdout  
                    ) 



class BlockedException(Exception):
	def __init__(self):
		Exception.__init__(self)

class weiboSpider:
	def __init__(self,username,password):
		self.username=username
		self.password=password
		try: 
			#login and build opener with cookie
			self.opener=self.login()
		except urllib2.HTTPError as e:
			print e
			exit()
		except Exception as e:
			print e
			exit()

	def login(self):
		#create cookie
		cookieJ = cookielib.CookieJar()
		#install cookie
	  	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJ))
		#pretend to be a browser
		opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.65 Safari/537.36')]
		#open login page
        	response=opener.open('http://login.weibo.cn/login/')
        	loginText=response.read()
       		Pyquery=pyquery.PyQuery(loginText)
		#get login url
       		loginURL=Pyquery('form').attr('action')
       		loginURL='http://login.weibo.cn/login/'+loginURL
		#get password key	
	       	password=Pyquery('input').eq(1)
	       	password=pyquery.PyQuery(password).attr('name')
		#get vk value
	        vk=Pyquery('input').eq(6).val()
		#wrap post data	
		data={'mobile':self.username,password:self.password,'remember':'on','vk':vk,'submit':'登录'}	
		#encode post data
	       	data=urllib.urlencode(data)
		#login
		response=opener.open(loginURL,data)
       		#<DEBUG>print response.geturl()
		if 'http://login.weibo.cn/' in response.geturl() :
			raise Exception("username or password is wrong")
		logging.info("user :"+self.username+" login sucesses")
		return opener

	#get the users he follows
	def getfollowing(self,userid):
		#list to store the people he follows
		followingList=[]
		
		#HTTPError may be raised
		req=self.opener.open('http://weibo.cn/'+userid+'/follow',timeout=5)
		# if blocked by sina, raise exception
		self.blockedCheck('weibo.cn/'+userid+'/follow',req.geturl())
		content=req.read()
		followingList.extend(self.extractFollowing(content))	

		#rest for a while
		restTime=self.randomRest()
		#logging
		logging.info('rested for '+str(restTime)+' collect from '+req.geturl())
		#extract next url
		while True:
			nextUrl=self.extractFollowingUrl(content)
			if nextUrl == None:
				break
			req=self.opener.open('http://weibo.cn'+nextUrl,timeout=5)
			self.blockedCheck('weibo.cn/'+userid+'/follow',req.geturl())
			content=req.read()
			#extract data
			followingList.extend(self.extractFollowing(content))
			#rest for a while
			restTime=self.randomRest()
			#logging
			logging.info('rested for '+str(restTime)+' collect from '+req.geturl())

		return followingList

	def blockedCheck(self,expectedURL,actualURL):
		if expectedURL not in actualURL:
			logging.info('user : '+self.username+' is blocked by Sina')
			raise BlockedException()
	
	def randomRest(self):
		restTime=random.random()*2+5
		time.sleep(restTime)
		return restTime		
	
	def extractFollowingUrl(self,content):
		html=pyquery.PyQuery(content)
		for ele in html('form a'):
			if pyquery.PyQuery(ele).text()==u'下页':
				return pyquery.PyQuery(ele).attr('href')
		return None

	#ATTENTION: Here assume spider follows nobody
	def extractFollowing(self,content):
		pageList=[]
		html=pyquery.PyQuery(content)
		for ele in html('table'):
			try:
				name=pyquery.PyQuery(ele)('td').eq(1)('a').eq(0).text()
				uid=pyquery.PyQuery(ele)('td').eq(1)('a').eq(1).attr('href').split('?')[1].split('&')[0].split('=')[1]
				fans=pyquery.PyQuery(ele)('td').text().split(' ')[1][2:-1]
				pageList.append(name+','+uid+','+fans)
			except AttributeError as e:
				print e 
				continue
		return pageList

if __name__ == '__main__':
	spider = weiboSpider('18612986170', '18612986170')
	print spider.getfollowing('3399558022')

