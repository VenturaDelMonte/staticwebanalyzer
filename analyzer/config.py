#!/usr/bin/env python
# file name: config.py
# created by: Ventura Del Monte 
# purpose: configuration loader 
# last edited by: Ventura Del Monte 18-11-2014

class ConfigManager:
	def __init__(self):
		self.config = {	}
	def get(self, key, default = None):
		try:
			return self.config[key]
		except KeyError:
			return default
	def getInt(self, key, default= None):
		return int(self.get(key, default))
	def getFloat(self, key, default= None):
		return float(self.get(key, default))
	def load(self, filename):
		with open(filename, "r") as file:
			for line in file:
				key, value = line.split("=")
				self.config[key.strip()] = value.strip()
	def getPairs(self):
		return self.config
	def updateConfig(self, newConfig = {}):
		self.config.update(newConfig)
	
