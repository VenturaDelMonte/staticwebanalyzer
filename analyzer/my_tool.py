#!/usr/bin/env python
# file name: my_tool.py
# created by: Ventura Del Monte 
# purpose: example tool 
# last edited by: Ventura Del Monte 23-07-2014

from tools import BaseTool

class MyTool(BaseTool):

	def __init__(self):
		BaseTool.__init__(self, "Hello")

	def run(self, browser):
		print "ok"
		