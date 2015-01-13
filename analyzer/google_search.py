#!/usr/bin/env python
# file name: google_search.py
# created by: Ventura Del Monte 
# purpose: Google Search Implementation 
# last edited by: Ventura Del Monte 04-10-2014

from internal_browser import *
from bs4 import BeautifulSoup
import urlparse
import re

class GoogleSearch(InternalBrowser):
#	base_url = "https://www.google.it/search?q="
	def __init__(self):
		InternalBrowser.__init__(self, usrAgent = ['windows7', 'firefox'])
		self.open("www.google.com")
	
	def search(self, query):
		data = self.queryForm('gbqf', 'q', query)
		html = BeautifulSoup(data)
		ret = []
		#for li in html.findAll(attrs = {'class' : re.compile("rc")}):
		for a in html.select('h3 > a'):
			href = a['href']
			ret.append((href, urlparse.urlparse(href)))
		return ret
		
	
