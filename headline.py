import urllib.request
from urllib.request import urlopen
import time
from lxml import etree
import bitly_api
import json
import follow_bot_db as fb
import random
from random import randint


def shorten_url(long_url):
	username = 'forexfiend' # use your Username/password 
	password = 'R_b7b8cdc2514f46ce89b7f9b49852debe'
	req_url = "http://api.bit.ly/v3/shorten?login={}&apiKey={}&longUrl={}&format=txt".format(username, password, long_url)
	#req_url = urlencode(bitly_url.format(username, password, long_url))
	short_url = urlopen(req_url).read().decode('utf-8')
	return short_url

#urls = ["http://wwww.dailyfx.com", "http://www.forexfactory.com/news.php", "http://www.forex.com", "http://www.fxstreet.com"]
headlines = []
def dailyFX():
	agent = 'Mozilla/5.0 (Linux; Android 4.4.2; LGMS323 Build/KOT49I.MS32310c) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.109 Mobile Safari/537.36'
	req = urllib.request.Request('http://www.dailyfx.com/', headers={ 'User-Agent': agent })
	html = urllib.request.urlopen(req).read()
	#print (html)
	html = etree.HTML(html)

	xpath= "//*[@class='secondary-boxes-header'][1]/a/@href"
	links = html.xpath( xpath )
	xpath = "//*[@class='secondary-boxes-header'][1]/a/text()"
	link_text = html.xpath( xpath )
	article_url = "http://www.dailyfx.com/{}".format(links[0])
	print( link_text[0],"\n",shorten_url(article_url) )

	if link_text[0] not in headlines:

		fb.api.update_status( "{} - {}".format( link_text[0], shorten_url(article_url) ) )
		print("status updated!\n")
		headlines.append(link_text[0])
	else:
		print("headline already used\n")



def fxFactory():
	agent = 'Mozilla/5.0 (Linux; Android 4.4.2; LGMS323 Build/KOT49I.MS32310c) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.109 Mobile Safari/537.36'
	req = urllib.request.Request('http://www.forexfactory.com/news.php', headers={ 'User-Agent': agent })
	html = urllib.request.urlopen(req).read()
	#print (html)
	html = etree.HTML(html)
	xpath= "//*[@class='story high large'][1]/span[1]/a/@href"
	links = html.xpath( xpath )
	#print(links)
	xpath = "//*[@class='story high large'][1]/span[1]/a/text()"
	link_text = html.xpath( xpath )

	article_url = "http://www.forexfactory.com/{}".format(links[0])
	print( link_text[0],"\n", article_url )

	if link_text[0] not in headlines:

		fb.api.update_status( "{} - {}".format( link_text[0], article_url ) )
		print("status updated!\n")
		headlines.append(link_text[0])
	else:
		print("headline already used\n")

def fxStreet():
	import re
	agent = 'Mozilla/5.0 (Linux; Android 4.4.2; LGMS323 Build/KOT49I.MS32310c) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.109 Mobile Safari/537.36'
	req = urllib.request.Request('http://www.fxstreet.com/news/forex-news/', headers={ 'User-Agent': agent })
	html = urllib.request.urlopen(req).read()
	html = etree.HTML(html)
	xpath = "//*[@class='list-item-content'][1]/a[1]/@href"
	headline_link = html.xpath( xpath )
	article_url = 'http://www.fxstreet.com/news/forex-news/{}'.format( re.sub('./', '', headline_link[0]) )
	xpath = "//*[@class='list-item-content'][1]/a[1]/text()"
	link_text = html.xpath( xpath )
	print( link_text[0], shorten_url(article_url) )

	if link_text[0] not in headlines:

		fb.api.update_status( "{} - {}".format( link_text[0], shorten_url(article_url) ) )
		print("status updated! \n")
		headlines.append(link_text[0])
	else:
		print("headline already used\n")



functions = [ fxStreet, fxFactory, dailyFX ]
def post_headline():
	rand = randint(0, 2)
	functions[rand]()

one_hour = 3600
while True:
	post_headline()
	time.sleep(random.uniform(1,3) * one_hour)
