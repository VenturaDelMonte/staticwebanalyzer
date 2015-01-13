#!/usr/bin/env python
# file name: main.py
# created by: Ventura Del Monte 
# purpose:  launcher class
# last edited by: Emiliano Di Marino 30-08-2014

import sys
import time
import random

from tools import BaseTool
from tools import ToolsManager
from internal_browser import InternalBrowser
from form_analyzer import BASE_WAIT_TIME

if __name__ == "__main__":

	# the file that contains the websites
	# must be passed through command line.
	# In this case it is called "websites.txt"
	file_name = sys.argv[1]
	
	# list that will contain the URLs
	URLs = []
	
	random.seed(time.time())

	manager = ToolsManager()

#	manager.register("test", "my_tool", "MyTool")
	manager.register("FormAnalyzer", "form_analyzer", "FormAnalyzer")
	#manager.register("WhoIs", "WhoIsTool", "WhoIsTool")
	#manager.register("SSLCertificateCheck", "SSLCertificateCheckTool", "SSLCertificateCheckTool")
	#manager.register("BannerTool", "BannerTool", "BannerTool")
	
	browser = InternalBrowser()
	
	#Read url from websites.txt
	url = sys.argv[1]
	print "open " + url
	browser.open(url)

	for tool in manager.yieldTools():
		print "processing " + tool.name
		
		toolBrowser = browser
		if tool.refreshNeeded():
			time.sleep(BASE_WAIT_TIME + random.randint(0, 5))
			toolBrowser = InternalBrowser()
			toolBrowser.open(url)
			
		tool.run(toolBrowser)

	
