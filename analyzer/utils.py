#!/usr/bin/env python
# file name: utils.py
# created by: Ventura Del Monte 
# purpose: helpers 
# last edited by: Ventura Del Monte 04-10-2014

import re
import urllib2

def isValidUrl(url):
	regex = re.compile(
		r'^(?:http|ftp)s?://' # http:// or https://
		r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
		r'localhost|' #localhost...
		r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
		r'(?::\d+)?' # optional port
		r'(?:/?|[/?]\S+)$', re.IGNORECASE)
	
	return regex.match(url)

def checkInternetConnection(url = 'http://74.125.228.100', tout = 1):
	try:
		response = urllib2.urlopen(url, timeout = tout) # google.com
		return True
	except urllib2.URLError as err:
		pass
	return False

class Dicty(dict):

	marker = object()
	
	def __init__(self, value = None):
		if value is None:
			pass
		elif isinstance(value, dict):
			for key in value:
				self.__setitem__(key, value[key])
		else:
			raise TypeError, "expected dict"
	
	def __setitem__(self, key, value):
		if isinstance(value, dict) and not isinstance(value, Dicty):
			value = Dicty(value)
		dict.__setitem__(self, key, value)
	
	def __getitem__(self, key):
		found = self.get(key, Dicty.marker)
		if found is Dicty.marker:
			found = Dicty()
			dict.__getitem__(self, key, found)
		return found
	
	__setattr__ = __setitem__
	__getattr__ = __getitem__
	
class WordsDictionary:
	def __init__(self, filename = "dict.dat"):
		self.data = []
		with open(filename, "r") as f:
			for line in f:
				if line != "":
					for w in line.split():
						self.data.append(w.replace("-", " "))
		f.close()
		#print self.data
	
	def next(self):
		for w in self.data:
			yield w
		
	



