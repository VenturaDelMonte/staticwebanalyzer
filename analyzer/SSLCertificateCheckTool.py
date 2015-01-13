#!/usr/bin/env python
# file name: SSLCertificateCheckTool.py
# created by: Ventura Del Monte
# purpose: Check the SSL certificate validity
# last edited by: Ventura Del Monte 18-10-2014

import urlparse

from tools import BaseTool
from tools import ToolException
from certificate_validator import CertificateValidator

class SSLCertificateCheckTool(BaseTool):

	def __init__(self, config):
		BaseTool.__init__(self, "SSLCertificateCheck", config)
		self.values = []
	
	# method return True if the certificate is valif, False otherwise
	def run(self, browser):
		url = browser.getUrl()
		url = 'https://' + url if not url.startswith('http') else url.replace('http:', 'https:') 
		parsed = urlparse.urlparse(url)
		hostname = "%s://%s" % (parsed.scheme, parsed.netloc)
		
		validator = CertificateValidator(browser.getUserAgent())
		err, cert = validator.validate(hostname)
		if len(cert) > 0:
			self.values = [ [k, v] for k, v in cert.iteritems() ]
			return False
		else:
			self.values = [ [ hostname, err] ]
			return not 'connection refused' in err.lower()
		

	
	def createModel(self):
		if len(self.values) > 0:
			return True, ["key", "value"],  self.values
		else:
			return True, [ "Status" ], [ [ "SSL Certificate is valid" ] ]
