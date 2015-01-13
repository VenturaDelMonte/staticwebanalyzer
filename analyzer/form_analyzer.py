#!/usr/bin/env python
# file name: form_analyzer.py
# created by: Ventura Del Monte 
# purpose: analyze forms
# last edited by: Ventura Del Monte 01-08-2014

from tools import BaseTool, ToolException
from internal_browser import InternalBrowser 
from multiprocessing.pool import ThreadPool
import time
import random 
from bs4 import BeautifulSoup
from utils import WordsDictionary
from utils import isValidUrl
from urllib2 import HTTPError, URLError
import collections
from certificate_validator import CertificateValidator

BASE_WAIT_TIME = 3
NO_WAIT = False
SINGLE_THREADED = False

wordsDict = WordsDictionary()
# it analyzes every form in the loaded page
def analyzeForms(browser, close = False):
	global wordsDict
	ret = {}
	#print "analyzing %s" % browser.url
	'''
	for form in browser.getForms():	
		if not form.action.startswith("https://"):
			print "Form [%s] without https action! May be suspicious!!" % form.action
			print str(form)		
			ret[form.action] = form
	'''
	soup = BeautifulSoup(browser.httpResponse)
	forms = soup.findAll('form')
	if len(forms) == 0 or not isinstance(forms, collections.Iterable):
		return ret
	for form in forms:
		action = form.get('action')
		if not action is None:
			if not action.startswith('http'):
				realAction = "%s/%s" % (browser.url, action)
			else:
				realAction = action
			
			#if (not realAction.startswith("https://")) and browser.url.startswith("https://"):
			#	continue
			#if realAction.startswith('https'):
			#	continue
			
			#print action, error
			innerHtml = form.decode_contents(formatter = 'html')
			for w in wordsDict.next():
				if innerHtml.find(w) > -1:
					ret[realAction] = not realAction.startswith('https')
					print action, "::", realAction
					break
	if close:
		browser.close()
	return ret



# makes a request to link
def processLink(link):
	try:
		if not isValidUrl(link):
			return {}
		if not NO_WAIT:
			time.sleep(BASE_WAIT_TIME + random.randint(0, 5))
		obj = InternalBrowser()
		obj.open(link)
		return analyzeForms(obj, True)
	except (HTTPError, URLError):
		return {}
	except Exception as e:
		raise ToolException(str(e) + " - " + link)


class FormAnalyzer(BaseTool):

	def __init__(self, config):
		super(FormAnalyzer, self).__init__("FormAnalyzer", config)
		self.unsafeForms = {}
		self.links = set()
		self.results = {}
		self.validator = CertificateValidator()
		self.httpTrafficTreshold = self.config.getInt("http_traffic_treshold", 20)
	
	# collect all links in a page
	def collectLinks(self, browser):
		for link in browser.getLinks():
			target = ""
			if link.url.startswith("mailto") or link.url.startswith("ftp") or link.url.startswith("telnet"):
				continue
			elif link.url.startswith("http"):
				#print link.url
				target = link.url
			else:
				#print "%s/%s" % (browser.url, link.url)
				target = "%s/%s" % (browser.url, link.url)
			if target.startswith(browser.url):
				self.links.add(target)
	
	def run(self, browser):
		global wordsDict
		try:
			ret = False
			self.validator.setUserAgent(browser.getUserAgent())
			self.collectLinks(browser)
			all = analyzeForms(browser)
			
			print "found %d links" % len(self.links)
			pool = ThreadPool(1 if SINGLE_THREADED else None)
			if len(self.links) < self.httpTrafficTreshold: #~ add a treshold for limiting http traffic
				temp = pool.map(processLink, list(self.links))
				map(lambda x : all.update(x), temp)

			self.results = { k : "Unsafe form" for k, v in all.iteritems() if v is True }
			
			def validateHttpsCertificate(item):
				print "validating https cert ", item
				return (str(item[0]), self.validator.validate(item[0]))
			
			def updateResultPredicate(e):
				if e[1][0] != "SSL Certificate is valid":
					self.results.update({e[0] : e[1][0]}) 

			certificateCheck = pool.map(validateHttpsCertificate, filter(lambda x : x[1] is False, all.iteritems()))
			map(updateResultPredicate, certificateCheck)

			if len(self.results) >= self.config.getInt("form_count_treshold", 1):
				ret = True

			print "res", self.results
				
		except Exception as e:
			#print e
			raise ToolException(str(e))
		
		return ret
#		for key in self.unsafeForms:
#			print "Form [%s] without https action! May be suspicious!!" % key
	
	def createModel(self):
		if len(self.results) > 0:
			return True, ["Form action", "Status"], [ [k, v] for k, v in self.results.iteritems() ]  
		else: 
			return True, ["Form action"], [ [ "No suspect forms" ] ]
		
	
	

