# file name: WhoIsTool.py
# created by: Anna De Angelis
# purpose:  WhoIs Tool
# last edited by: Anna De Angelis 20-10-2014

# INSTALL IPWHOIS, GOOGLEMAPS, PYGMAPS, IPADDR


import socket, math, urllib
from tools import BaseTool
from ipwhois import IPWhois
from pprint import pprint
from pygmaps import pygmaps
import urlparse
from tools import ToolException

class WhoIsTool(BaseTool):

	def __init__(self, config):
		BaseTool.__init__(self, "WhoIs", config)
		self.values = []
		
	def processUrl(self, url):
		
		url = 'https://' + url if not url.startswith('http') else url.replace('http:', 'https:')
		#print ('pp ' + url)
		parsed = urlparse.urlparse(url)
		hostname = "%s://%s" % (parsed.scheme, parsed.netloc)
		url = url.split("//")[1]
		url_s = url.split("/")[0]
		ip = socket.gethostbyname(url_s)
		#get Whois' informations
		obj = IPWhois(ip)
		result = obj.lookup()
		
		addr = result['nets'][0]['address'] 
		country = result['nets'][0]['country']
		'''
		self.values.append(["NEW ITEM", "STARTS HERE"])
		self.values.append(["Url", url])
		self.values.append(["Address",  addr])
		self.values.append(["Name",  result['nets'][0]['name'] ])
		self.values.append(["State",  result['nets'][0]['state'] ])
		self.values.append(["City",  result['nets'][0]['city']])
		self.values.append(["Description",  result['nets'][0]['description']])
		self.values.append(["Country",  country])
		'''
		
		# Encode query string into URL
		url_map = 'http://maps.google.com/?q=' + urllib.quote(addr) #+ '&output=js'
		
		
		#self.values.append(["Link on GMaps", url_map])
		domain = '.'+url_s.split('.')[-1]
		if domain == '.com':
			print('It is .com!')
			
		map = {'.it' : 'Italy, Italia, it' ,'.es' : 'Spagna, Espana, Es', '.us' : 'us , State Unite, Stati Uniti', '.uk' : 'uk, gb, united kingdom', '.co':'co', '.cn' : 'cina, ci, china', '.hk':'hong kong, giappone, japan','.mo': 'macau'}
		if country != 'None':
			if map.get(domain) != None:
				if country.lower() in map[domain].lower():
					results = "It is ok!! Domain and country coincide!"
					print(results)
				else:
					results = "Something is wrong! Domain and country don t coincide!" 
					print(results)
			else:
				results = "Domain not defined"
				print(results)
		#self.values.append(["Results",  results])
		
		temp = {
			"Url" : url,
			"Address" : addr,
			"Name" : result['nets'][0]['name'],
			"State" : result['nets'][0]['state'],
			"City" : result['nets'][0]['city'],
			"Description" : result['nets'][0]['description'],
			"Country" : country,
			"Link on GMaps" : url_map,
			"Results" : results
		}
		
		self.values.append({ "entry #%d" % (len(self.values)) : temp })
		
		
	def run(self, browser):
		try:
			for url in browser.getRedirections():
				self.processUrl(url)
		except Exception as e:
			raise ToolException(str(e))
		return False
			
		
	def createModel(self):
		return False, ["key", "value"], self.values


	
