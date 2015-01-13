#!/usr/bin/env python
# file name: redirect_tool.py
# created by: Ventura Del Monte
# purpose: http 30x redirection analysis 
# last edited by: Ventura Del Monte 18-10-2014

from tools import BaseTool
from tools import ToolException

class RedirectionAnalyzer(BaseTool):

	def __init__(self, config):
		super(RedirectionAnalyzer, self).__init__("RedirectionAnalyzer", config)
		self.values = []
	
	def run(self, browser):
		redir = browser.getRedirections()
		self.values = [ [url, code] for url, code in redir.iteritems() if not code is False ] if len(redir) > 0 else [ [ browser.gerUrl(), "No redirections" ] ]
		return len(self.values) > self.config.getInt("http_redirect_treshold", 5)
	
	def createModel(self):
		return True, [ "Url", "Code" ], self.values
	

