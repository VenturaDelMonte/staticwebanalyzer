#!/usr/bin/env python
# file name: certificate_validator.py
# created by: Ventura Del Monte 
# purpose: SSL certificate validation
# last edited by: Ventura Del Monte 17-10-14

# more details here:
# http://curl.haxx.se/libcurl/c/CURLOPT_SSL_VERIFYPEER.html
# http://curl.haxx.se/libcurl/c/CURLOPT_SSL_VERIFYHOST.html

# https://github.com/pycurl/pycurl/blob/master/tests/certinfo_test.py

import pycurl
import utils

def dummy(*args):
	pass

class CertificateValidator:

	defaultCurlOptions = [
		(pycurl.SSL_VERIFYPEER, 1),
		(pycurl.SSL_VERIFYHOST, 2),
		(pycurl.FOLLOWLOCATION, 1),
		(pycurl.CAINFO, "./ssl/curl-ca-bundle.crt"),
		(pycurl.OPT_CERTINFO, 1),
		(pycurl.WRITEFUNCTION, dummy)
	]

	def __init__(self, userAgent = 'libcurl'):
		self.curl = pycurl.Curl()
		assert hasattr(self.curl, 'OPT_CERTINFO')
		for opt in self.defaultCurlOptions:
			#print opt
			self.curl.setopt(*opt)
		self.curl.setopt(pycurl.USERAGENT, userAgent)
	
	def close(self):
		self.curl.close()
	
	def setUserAgent(self, userAgent):
		self.curl.setopt(pycurl.USERAGENT, userAgent)
	
	def validate(self, url):
		try:
			self.curl.setopt(pycurl.URL, url)
			self.curl.perform()
			cert = self.curl.getinfo(pycurl.INFO_CERTINFO)
		except pycurl.error as e:
			print e
			return e[1], {}
		return "SSL Certificate is valid", self.parseCertificate(cert)
	
	def parseCertificate(self, data):
		return {entry[0] : entry[1] for entry in data[0] if entry[0] != "Signature" and entry[0] != "Cert"}
	



