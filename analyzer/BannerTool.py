#FILE NAME: BannerTool.py
#created by: Ciro Veneruso
#purpose: banner localization
#last edited by: Ciro Veneruso

#INSTALL: BeautifulSoup

#TODO: this code is a blob, must be refactorized!!!!


import re
import mechanize
import socket
import urllib
from tools import BaseTool
from bs4 import BeautifulSoup
from pprint import pprint
from ipwhois import IPWhois, WhoisLookupError
from tld import get_tld
import urlparse
from tld.exceptions import TldIOError, TldDomainNotFound, TldBadUrl
from tools import ToolException

class BannerTool(BaseTool):
	  
	def __init__(self, config):
		  BaseTool.__init__(self, "BannerAnalyzer", config, needRefresh = True) 
		  self.values = []
	def run(self, browser):
		try:
			url = browser.url.replace('http://','')
			print url+"\n"
			#response = browser.open(url)
			html = browser.httpResponse #response.get_data()
			site_domain_name = get_tld(browser.url)
			#print(site_domain_name)
			soup = BeautifulSoup(html)
			links = soup.findAll('a')
			response_domain = ""
			addr = ""
			name = ""
			state = ""
			city = ""
			description = ""
			country = ""
			foo_flag = 0
			flag = 0
			for link in links:
				foo = link.findChild('img')
				#print foo
				if foo is not None:
					foo_flag = 1
					flag = 1
					href = link.get('href')
					if href is None:
						continue
					print(href+"\n")
					if href.startswith('/'):
						response_domain ="link interno"
						print ("link interno\n")
					elif href.startswith('/'):
						response_domain ="Link interno"
						print ("link interno\n")
					elif href.startswith("http://"+url):
						response_domain ="link interno"
						print ("link interno\n")
					elif href.startswith("https://"+url):
						response_domain ="link interno"
						print ("link interno\n")
					else:
						response_domain ="link esterno"
						print ("link esterno... Geolocalizzazione:\n")
						try:
							banner_domain_name = get_tld(href)
							print(banner_domain_name+"\n")
							print(site_domain_name)
							
							
							url = 'https://' + url if not banner_domain_name.startswith('http') else banner_domain_name.replace('http:', 'https:')

							parsed = urlparse.urlparse(url)
							hostname = "%s://%s" % (parsed.scheme, parsed.netloc)
							url = url.split("//")[1]
							url_s = url.split("/")[0]
							ip = socket.gethostbyname(url_s)
							
							
							#print(href)
							#get ip by url
							#ip = socket.gethostbyname(banner_domain_name)
							#get information by ip
							result = None
							try:
								obj = IPWhois(ip)
								result = obj.lookup()
							except Error as e:
								continue
							addr = result['nets'][0]['address'] if result['nets'][0]['address'] != None else 'None' 
							name = result['nets'][0]['name'] if result['nets'][0]['name'] != None else 'None'
							state = result['nets'][0]['state'] if result['nets'][0]['state'] != None else 'None'
							city = result['nets'][0]['city'] if result['nets'][0]['city'] != None else 'None'
							description = result['nets'][0]['description'] if result['nets'][0]['description'] != None else 'None'
							country = result['nets'][0]['country'] if result['nets'][0]['country'] != None else 'None'
							'''
							self.values.append(["Link analyzed",href])
							self.values.append(["Response",response_domain])
							self.values.append(["Address",  addr])
							self.values.append(["Name",  name])
							self.values.append(["State",  state])
							self.values.append(["City",  city])
							self.values.append(["Description",  description])
							self.values.append(["Country",  country])
							print('Name: ' + name + '\n' + 'Description: ' + description + '\n' + 'Address: ' +
								addr + '\n' + 'Country: ' + country + '\n' + 'State: ' + state + '\n' + 'City: ' + city)
							'''

							temp = {
								"Url" : url,
								"Address" : addr,
								"Name" : name,
								"State" : state,
								"City" : city,
								"Description" : description,
								"Country" : country,
								"Response" : response_domain
							}
							self.values.append({ "Link analyzed %s" % (href) : temp })	
						except TldBadUrl as e:
							print ("Bad URL!")
					if flag == 0:
						print("There aren' t extra domain banners in this site") 
				
			if(foo_flag == 0):
				print("There aren't banner in this site")
		except WhoisLookupError as e:
			raise ToolException(str(e))

		return len(self.values) >= self.config.getInt("banner_count_treshold", 0)

	def createModel(self):
		return False, ["key","value"], self.values
