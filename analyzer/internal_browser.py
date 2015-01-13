#!/usr/bin/env python
# file name: internal_browser.py
# created by: Ventura Del Monte 
# purpose: browser internal class 
# last edited by: Ventura Del Monte 23-07-2014

# READ MECHANIZE DOCUMENTATION BEFORE ASKING ANYTHING :D

import mechanize
import cookielib
from user_agents import *

class InternalBrowser(object):

	dbgMode = False
	userAgent = None
	browser = None
	cookieLib = None
	httpResponse = None

	def __init__(self, dbgMode = False, usrAgent = None, addHeaders = []):
		self.userAgent = None
		self.url = None
		self.redirections = {}
		self.browser = mechanize.Browser()
		# setting cookie jar
		self.cookieLib = cookielib.LWPCookieJar()
		self.browser.set_cookiejar(self.cookieLib)
		# Browser options
		self.browser.set_handle_equiv(True)
		self.browser.set_handle_gzip(False) #~ was True
		self.browser.set_handle_redirect(True, self.onRedirect)
		self.browser.set_handle_referer(True)
		self.browser.set_handle_robots(False)
		# Follows refresh 0 but not hangs on refresh > 0
		self.browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time = 1)
		# Want debugging messages?
		self.browser.set_debug_http(dbgMode)
		self.browser.set_debug_redirects(dbgMode)
		self.browser.set_debug_responses(dbgMode)
		self.browser.set_debug_redirects(dbgMode)
		self.dbgMode = dbgMode
		# User-Agent
		self.selectUserAgent(usrAgent)
		headers = addHeaders
		headers.append(('User-agent', self.userAgent))
		self.browser.addheaders = headers 
	
	def getUrl(self):
		return self.browser.geturl()
	
	# userAgent passed argument should be a list like [ 'linux', 'firefox' ]	
	def selectUserAgent(self, userAgent):
		if userAgent == None:
			self.userAgent = getLatestUserAgent('windows7', 'firefox') # AGENTS['linux']['firefox']
		else:
			self.userAgent = getLatestUserAgent(userAgent[0], userAgent[1])
		if self.dbgMode:
			print "user agent:", self.userAgent
	
	def getUserAgent(self):
		return self.userAgent 
	
	# it makes an http request to url and retrieves the reply
	def open(self, url):
		if not url.startswith("http"):
			url = "http://" + url
		self.url = url
		self.redirections = { url : False }
		self.httpResponse = self.browser.open(url)
		return self.httpResponse
	
	def close(self):
		self.browser.close()
	
	# it retuns response full content as string
	def getPlainHtml(self):
		if self.httpResponse == None:
			raise RuntimeError("no response, you forgot to open site...")
		return self.httpResponse.read()
	
	# it yields every form object found in response body
	def getForms(self):
		if self.httpResponse == None:
			raise RuntimeError("no response, you forgot to open site...")
		forms = self.browser.forms()
		for obj in forms:
			yield obj 
	
	# it yields every link object found in response body
	def getLinks(self):
		if self.httpResponse == None:
			raise RuntimeError("no response, you forgot to open site...")
		links = self.browser.links()
		for obj in links:
			yield obj 
	
	def getLinksList(self):
		if self.httpResponse == None:
			raise RuntimeError("no response, you forgot to open site...")
		ret = []
		for a in self.browser.links():
			ret.append(a)
		return ret
	
	def getHttpResponse(self):
		if self.httpResponse == None:
			raise RuntimeError("no response, you forgot to open site...")
		return self.httpResponse
	
	def queryForm(self, formName, textArea, query):
		if self.httpResponse == None:
			raise RuntimeError("no response, you forgot to open site...")
		self.browser.select_form(name = formName)
		self.browser.form[textArea] = query
		data = self.browser.submit()
		return data.read()
	
	def onRedirect(self, request, code, newUrl):
		print request, code, newUrl
		self.redirections[newUrl] = code
	
	def getRedirections(self):
		return self.redirections
