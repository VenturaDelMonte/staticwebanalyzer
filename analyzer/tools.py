#!/usr/bin/env python
# file name: tools.py
# created by: Ventura Del Monte 
# purpose: tool base class, tool registrator 
# last edited by: Ventura Del Monte 23-07-2014


class BaseTool(object):
	name = ""
	needRefresh = False
	description = ""
	config = None
	def __init__(self, name, config = None, needRefresh = False, description = ""):
		self.name = name
		self.config = config
		self.description = description
		self.needRefresh = needRefresh
		
	def refreshNeeded(self):		
		return self.needRefresh
	
	def run(self, browser):
		pass
	
	def createModel(self):
		pass
	

class ToolException(RuntimeError):
	def __init__(self, message = "", errors = {}):
		RuntimeError.__init__(self, message)
		self.errors = errors

class ToolsManager:
	''' class for managing the different handlers registered '''
	def __init__(self, cfg):
		self.tools = {}
		self.cfg = cfg
	
	def count(self):
		return len(self.tools)

	def registeredToolsByName(self):
		return self.tools.keys()
	
	def register(self, name, module, className):
		''' register a new tool by its name, module has to be a valid py file, tool has to be the class for processing '''
		mod = __import__(module)
		self.tools[name] = getattr(mod, className)
	
	def getByName(self, name):
		''' retrieves the tool for registered name '''
		try:
			handle = self.tools[name](config = self.cfg)
			return handle
		except KeyError:
			raise Exception("not registered tool [%s]" % name)
	
	def yieldTools(self):
		for tool in self.tools:
			print tool
			yield self.tools[tool](config = self.cfg)
	
	def yieldToolsNames(self):
		for tool in self.tools:
			yield tool
		
	




