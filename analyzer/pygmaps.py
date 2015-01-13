# file name: pygmaps.py
# created by: Anna De Angelis
# purpose:  Google map python wrapper
# last edited by: Anna De Angelis 01-08-2014
import math

class pygmaps:

	#initialize a map  with latitude and longitude of center point; returns the instant of pygmaps  
	def __init__(self, centerLat, centerLng, zoom ):
		self.center = (float(centerLat),float(centerLng))
		self.zoom = int(zoom)
		self.points = []
		self.coloricon = 'http://chart.apis.google.com/chart?cht=mm&chs=12x16&chco=FFFFFF,XXXXXX,000000&ext=.png'


	#add a point into a map and dispaly it, color is optional default is red; 
	# HTML COLOR CODE:  http://www.computerhope.com/htmcolor.htm
	def addpoint(self, lat, lng, color = '#FF0000'):
		self.points.append((lat,lng,color[1:]))

	#create the html file which inlcude one google map and all points and paths
	def draw(self, htmlfile):
		f = open(htmlfile,'w')
		f.write('<html>\n')
		f.write('<head>\n')
		f.write('<meta name="viewport" content="initial-scale=1.0, user-scalable=no" />\n')
		f.write('<meta http-equiv="content-type" content="text/html; charset=UTF-8"/>\n')
		f.write('<title>Google Maps - pygmaps </title>\n')
		f.write('<script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false"></script>\n')
		f.write('<script type="text/javascript">\n')
		f.write('\tfunction initialize() {\n')
		self.drawmap(f)
		self.drawpoints(f)
		f.write('\t}\n')
		f.write('</script>\n')
		f.write('</head>\n')
		f.write('<body style="margin:0px; padding:0px;" onload="initialize()">\n')
		f.write('\t<div id="map_canvas" style="width: 100%; height: 100%;"></div>\n')
		f.write('</body>\n')
		f.write('</html>\n')		
		f.close()

	
	def drawpoints(self,f):
		for point in  self.points:
			self.drawpoint(f,point[0],point[1],point[2])


	#############################################
	#          Low level Map Drawing            # 
	#############################################
	
	def drawmap(self, f):
		f.write('\t\tvar centerlatlng = new google.maps.LatLng(%f, %f);\n' % (self.center[0],self.center[1]))
		f.write('\t\tvar myOptions = {\n')
		f.write('\t\t\tzoom: %d,\n' % (self.zoom))
		f.write('\t\t\tcenter: centerlatlng,\n')
		f.write('\t\t\tmapTypeId: google.maps.MapTypeId.ROADMAP\n')
		f.write('\t\t};\n')
		f.write('\t\tvar map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);\n')
		f.write('\n')



	def drawpoint(self,f,lat,lon,color):
		f.write('\t\tvar latlng = new google.maps.LatLng(%f, %f);\n'%(lat,lon))
		f.write('\t\tvar img = new google.maps.MarkerImage(\'%s\');\n' % (self.coloricon.replace('XXXXXX',color)))
		f.write('\t\tvar marker = new google.maps.Marker({\n')
		f.write('\t\ttitle: "no implimentation",\n')
		f.write('\t\ticon: img,\n')
		f.write('\t\tposition: latlng\n')
		f.write('\t\t});\n')
		f.write('\t\tmarker.setMap(map);\n')
		f.write('\n')
		
	