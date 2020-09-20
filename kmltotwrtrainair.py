#!/usr/bin/env python
import xml.etree.ElementTree as ET
import re, math

#This program takes a KML file and converts it to .apt files for TWRTrainer
#Structure of KML should be as follows:
# TowerTrainer
	# AirportFiles
		# ICAO
			# magnetic variation=16
			# ...
			# runway
				# 18/36
					# displaced threshold=0/0
					# turnoff=left
					# LineString
				# ...
			# taxiway
				# A
					# LineString
				# ...
			# parking
				# A1
					# Point
				# ...
			# hold
				# A1H
					# Point
				# ...
		# ...

def getsegments(pdict, coordlist, startindex):
	# pdict, rawcoordlist, segments[pdict['name']]
	segments = []
	index = startindex
	basename = pdict['name']
	lastcoord = coordlist[0]
	for coord in coordlist[1:]:
		thisd = pdict.copy()
		thisd['name'] = basename+"/"+str(index)
		segments.append([thisd, [lastcoord, coord]])
		lastcoord = coord
		index+=1
	return segments, index

#This takes a single string and parses key=value lines into dict
def desctodict(desc):
	descdict={}
	lines = desc.split('\n')
	#print(lines)
	for line in lines:
		#print(line)
		#Split by equals and add to dictionary
		assign = line.split('=')
		if len(assign)>1:
			descdict[assign[0]]=assign[1]
	return descdict

#Unused for now, could find nearest airports and stuff
def cosinedist(coord1,coord2): #Use cosine to find distance between coordinates
	lat1,lon1 = coord1
	lat2,lon2 = coord2
	phi1 = math.radians(lat1)
	phi2 = math.radians(lat2)
	dellamb = math.radians(lon2-lon1)
	R = 3440.06479 # Nmi
	# gives d in Nmi
	d = math.acos( math.sin(phi1)*math.sin(phi2) + math.cos(phi1)*math.cos(phi2) * math.cos(dellamb) ) * R
	#print("    Found distance "+str(d))
	return d

def ddtodms(lat, lon):
    # Convert decimal degrees to the sct2 format of [NSEW]DDD.MM.SS.SSS
    # First get the NSEW directions
    latdir = "N" if lat > 0 else "S"
    londir = "E" if lon > 0 else "W"
    # Take out any negatives
    lat = abs(lat)
    lon = abs(lon)
    # Round down to integers
    latdeg = int(lat)
    londeg = int(lon)
    # Get minutes
    latdmin = (lat-latdeg)*60
    londmin = (lon-londeg)*60
    # Get seconds
    latdsec = (latdmin - int(latdmin))*60
    londsec = (londmin - int(londmin))*60
    # Assemble the strings
    latstr = "%s%03.f.%02.f.%06.3f" % (latdir, latdeg, int(latdmin), latdsec)
    lonstr = "%s%03.f.%02.f.%06.3f" % (londir, londeg, int(londmin), londsec)
    # Return the lat lon pair in VRC format
    #coordstr = latstr + " " + lonstr
    return (latstr, lonstr)

class ttairport:

	def __init__(self, name, sats = [], pricao = None):
		self.name = name
		self.pricao = pricao
		self.parking = []
		self.runway = []
		self.taxiway = []
		self.hold = []
		self.dd = {}
		self.sats = sats

	def assimilate(self, thisairport):
		self.runway.extend(thisairport.runway)
		if thisairport.name == self.pricao:
			self.parking.extend(thisairport.parking)
			self.taxiway.extend(thisairport.taxiway)
			self.hold.extend(thisairport.hold)
			self.dd = thisairport.dd # Use primary airport data
		else:
			for t in thisairport.taxiway:
				self.taxiway.append([thisairport.name[1]+t[0], t[1]])
			for p in thisairport.parking:
				self.parking.append([thisairport.name[1]+p[0], p[1]])
			for h in thisairport.hold:
				self.hold.append([thisairport.name[1]+h[0], h[1]])

	def writefile(self):
		with open(self.name+".apt","w") as airfile:
			#Write the variables
			#airfile.write("icao=KPDX"\n")
			for key,val in self.dd.items():
				airfile.write(key+"="+val+"\n")
			# airfile.write("magnetic variation="+magvar+"\n")
			# airfile.write("field elevation="+fieldelev+"\n")
			# airfile.write("pattern elevation="+patternelev+"\n")
			# airfile.write("pattern size="+patternsz+"\n")
			# airfile.write("initial climb props="+initclbp+"\n")
			# airfile.write("initial climb jets="+initclbj+"\n")
			# airfile.write("jet airlines="+jetairlines+"\n")
			# airfile.write("turboprop airlines="+tpropairlines+"\n")
			# airfile.write("registration="+reg+"\n\n")
			airfile.write("\n")

			#Now write all the features

			for spot in self.parking:
				airfile.write("[PARKING "+spot[0]+"]\n")
				airfile.write(spot[1][0]+" "+spot[1][1]+"\n\n")

			for rwy in self.runway:
				airfile.write("[RUNWAY "+rwy[0]['name']+"]\n")
				if 'displaced threshold' in rwy[0].keys():
					airfile.write("displaced threshold="+rwy[0]['displaced threshold']+"\n")
				airfile.write("turnoff="+rwy[0]['turnoff']+"\n")
				for node in rwy[1]:
					airfile.write(node[0]+" "+node[1]+"\n")
				airfile.write("\n")

			for twy in self.taxiway:
				airfile.write("[TAXIWAY "+twy[0]+"]\n")
				#print(twy[1])
				for node in twy[1]:
					airfile.write(node[0]+" "+node[1]+"\n")
				airfile.write("\n")

			for hold in self.hold:
				airfile.write("[HOLD "+hold[0]+"]\n")
				airfile.write(hold[1][0]+" "+hold[1][1]+"\n\n")

class eseairport:

	def __init__(self, name):
		self.name = name
		self.taxi = []
		self.runway = []
		self.exit = []

	def writefile(self):
    # EXIT:<RWY name>:<exit name>:<direction>:<maximum speed>
    # TAXI:<TWY name>:<maximum speed>[:<usage flag>][:<gate name>]
    # COORD:<latitude>:<longitude>
		if self.taxi or self.exit:
			print("Writing ESE for "+self.name)
			#print(self.taxi)
			with open(self.name+".ese","w") as airfile:
				nodes = []
				airfile.write("[GROUND]\n")
				#Now write all the features
				for ex in self.exit:
					#print("Writing exit "+ex[0]['name']+": "+str(ex[0]))
					if 'maxspeed' in ex[0].keys():
						maxspd = ex[0]['maxspeed']
					else:
						maxspd = "20"
					if not 'runway' in ex[0].keys():
						print("Missing runway for exit "+ex[0]['name'])
					ei = ["EXIT", ex[0]['runway'], ex[0]['name'], ex[0]['direction'], maxspd]
					airfile.write(":".join(ei)+"\n")
					i = 0
					for node in ex[1]:
						if len(nodes) == 0:
							nodes.append(node)
						elif i==0 or i==len(ex[1])-1:
							for pnode in nodes:
								if cosinedist(pnode,node) < 8/6076:
									#print("Fusing point on exit "+ex[0]['name'])
									node = pnode
									break
							else:
								#print("Not fusing point on exit "+ex[0]['name'])
								nodes.append(node)
						coords = ddtodms(*node)
						airfile.write("COORD:"+coords[0]+":"+coords[1]+"\n")
						i+=1
					#airfile.write("\n")

				for twy in self.taxi:
					#print("Writing twy "+twy[0]['name']+": "+str(twy[0]))
					if 'maxspeed' in twy[0].keys():
						maxspd = twy[0]['maxspeed']
					else:
						maxspd = "20"
					ti = ["TAXI", twy[0]['name'], maxspd]
					if 'flg' in twy[0].keys():
						ti.append(twy[0]['flg'])
					if 'gate' in twy[0].keys():
						ti.append(twy[0]['gate'])
					airfile.write(":".join(ti)+"\n")
					#print(twy[1])
					i=0
					for node in twy[1]:
						if len(nodes) == 0:
							nodes.append(node)
						elif i==0 or i==len(ex[1])-1:
							for pnode in nodes:
								if cosinedist(pnode,node) < 8/6076:
									#print("Fusing point on twy "+twy[0]['name'])
									node = pnode
									break
							else:
								#print("Not fusing point on twy "+twy[0]['name'])
								nodes.append(node)
						coords = ddtodms(*node)
						airfile.write("COORD:"+coords[0]+":"+coords[1]+"\n")
						i+=1
					#airfile.write("\n")
		else:
			print("Not writing ESE for "+self.name)

#Default descriptions in case we can't read one
#Mostly for testing?
defaultdesc={
	"magnetic variation":"16", #Find for general area
	"field elevation":"20", #Should be figured out somehow
	"pattern elevation":"1020", #Based on field elev
	"pattern size":"1",
	"initial climb props":"3000", #Probably based on field elev
	"initial climb jets":"5000", #Probably based on field elev
	"jet airlines":"AAL,ACA,AWE,BAW,BLR,BTA,CAL,CAX,COA,CVA,DAL",
	"turboprop airlines":"EGF,USA,COA,CJC,JZA",
	"registration":"N"
}
defaultrwy={
	"displaced threshold":"0/0",
	"turnoff":"left"
}
defaultdict={
	"spd": "20",
	"flg": "1"
}
#Default aircraft for situations
#Name, coords, and alt taken from the point
#Unused at this time
#Callsign:Type:Engine:Rules:Dep Field:Arr Field:Crz Alt:Route:Remarks:Sqk Code:Sqk Mode:Lat:Lon:Alt:Speed:Heading
defaultac={
	"Type":"C172",
	"Engine":"P",
	"Rules":"V",
	"Crz Alt":"3000",
	"Route":"VFR",
	"Remarks":"/v/",
	"Sqk Code":"1200",
	"Sqk Mode":"S",
	"Speed":"0",
	"Heading":"180"
}

ttapts = {}
eapts = {}
tracons = [('P80','KPDX',("KPDX", "KTTD", "KHIO", "KSPB", "KUAO", "KVUO")),]
tracons.append(('S46','KSEA',("KSEA", "KBFI")))
for t in tracons:
	ttapts[t[0]] = ttairport(t[0], t[2], t[1])
	eapts[t[0]] = eseairport(t[0])

#The code is highly nested so if any step fails it just stops processing that part
#File will be written if at least ICAO is read, but could be empty
ns = {'egc': 'http://www.opengis.net/kml/2.2'}
tree = ET.parse('TowerTrainer.kml')
root = tree.getroot()
for document in root: #Root contains a document tag
	#print(document.tag)
	for docitem in document: #Document contains styles and folders
		#print(" "+docitem.tag)
#		if docitem.tag=="egc:Folder":
		#Get the name of each item in the main document
		elnameo=docitem.findall("egc:name",ns)
		#if len(elnameo)>0:
			#print(elnameo[0].text)
		#Looking for the one named as follows
		if len(elnameo)>0 and elnameo[0].text=="TowerTrainer":
			#Broken down into files by type of data
			for trainertype in docitem:
				#print("  "+trainertype.tag)
				#Look for one called as follows
				#These are the airport files defining the airport layout
				elnameo=trainertype.findall("egc:name",ns)
				if len(elnameo)>0 and elnameo[0].text=="AirportFiles":
					#Process each airport folder
					for airport in trainertype:
						#print("  "+airport.tag)
						#Name should be icao, could also use from the description
						elicao=airport.findall("egc:name",ns)
						if len(elicao)>0:
							icao = elicao[0].text
							print("Processing: "+icao)
							#print("  "+icao)
							#Read description tag for the folder
							thisairport = ttairport(icao)
							eairport = eseairport(icao)
							segments={}
							eldesc=airport.findall("egc:description",ns)
							if len(eldesc)>0:
								#Make iterable of the lines
								thisairport.dd=desctodict(eldesc[0].text)
							else: #If no description, use defaults
								thisairport.dd=defaultdesc
							#Each category will be one of the above
							for category in airport:
								#print("   "+category.tag)
								#Get name of this folder/category
								elcategory=category.findall("egc:name",ns)
								if len(elcategory)>0:
									type=elcategory[0].text
									#print("   "+type)
									#Look for the valid types of features
									if type in ["runway","taxiway","parking","hold","taxi","exit"]:
										for pmark in category:
											#print("    "+pmark.tag)
											#Get name
											elpmname=pmark.findall("egc:name",ns)
											if len(elpmname)>0:
												pmname=elpmname[0].text
												#Handle runways and taxiways together as they're both lines
												if type=="runway" or type=="taxiway":
													ellin=pmark.findall("egc:LineString",ns)
													if len(ellin)>0:
														for line in ellin:
															#print("     "+line.tag)
															elcoord=line.findall("egc:coordinates",ns)
															#Grab list of coordinates
															if len(elcoord)>0:
																rawcoordlist=[[i.strip().split(',')[1],i.strip().split(',')[0]] for i in elcoord[0].text.strip().split(' ') if i!='']
																#print(rawcoordlist)
																#print("     coordlist")
																#Save to runways list as dict of properties and list of coords
																if type=="runway":
																	eldesc=pmark.findall("egc:description",ns)
																	#Description holds a couple needed items
																	if len(eldesc)>0:
																		rwydict=desctodict(eldesc[0].text)
																	else: #Defaults
																		rwydict=defaultrwy.copy()
																	#Already got this so just add it
																	rwydict["name"]=pmname
																	thisairport.runway.append([rwydict,rawcoordlist])
																elif type=="taxiway": #Save to taxiway name and list of coords
																	thisairport.taxiway.append([pmname,rawcoordlist])
												#Handle parking and holds together as they're both points
												elif type=="parking" or type=="hold":
													elpts=pmark.findall("egc:Point",ns)
													#Get the coordinates
													if len(elpts)>0:
														for pt in elpts:
															#print("     "+pt.tag)
															elcoord=pt.findall("egc:coordinates",ns)
															if len(elcoord)>0:
																coords=elcoord[0].text.strip().split(',')
																latlon=[coords[1],coords[0]]
																#print("     "+coords)
																#Add to list as name and coords
																if type=="parking":
																	thisairport.parking.append([pmname,latlon])
																elif type=="hold":
																	thisairport.hold.append([pmname,latlon])
																#print(parkings)
												elif type=="taxi" or type=="exit":
													#print("Found ese placemark for "+pmname)
													ellin=pmark.findall("egc:LineString",ns)
													if len(ellin)>0:
														for line in ellin:
															#print("     "+line.tag)
															elcoord=line.findall("egc:coordinates",ns)
															#Grab list of coordinates
															if len(elcoord)>0:
																rawcoordlist=[[float(i.strip().split(',')[1]),float(i.strip().split(',')[0])] for i in elcoord[0].text.strip().split(' ') if i!='']
																#print(rawcoordlist)
																#print("     coordlist")
																#Save to runways list as dict of properties and list of coords
																eldesc=pmark.findall("egc:description",ns)
																#Description holds a couple needed items
																if len(eldesc)>0:
																	pdict=desctodict(eldesc[0].text)
																else: #Defaults
																	pdict=defaultdict.copy()
																#Already got this so just add it
																pdict["name"]=pmname
																#print("    Writing dict: "+str(pdict))
																if type=="exit":
																	eairport.exit.append([pdict,rawcoordlist])
																elif type=="taxi":
																	if "segment" in pdict.keys():
																		#if "number" in pdict.keys() and pdict['number'] == "yes":
																		if not pdict['name'] in segments.keys():
																			segments[pdict['name']] = 1
																		startindex = segments[pdict['name']]
																		#else:
																		#	startindex = None
																		segs, segments[pdict['name']] = getsegments(pdict, rawcoordlist, startindex)
																		for seg in segs:
																			eairport.taxi.append(seg)
																	else:
																		eairport.taxi.append([pdict,rawcoordlist])
									else:
										print("Did not recognize category: "+type)
							#We're done with all the features here
							for tracon in tracons:
								if icao in ttapts[tracon[0]].sats:
									ttapts[tracon[0]].assimilate(thisairport)
							ttapts[icao]=thisairport
							eapts[icao]=eairport
				elif len(elnameo)>0 and elnameo[0].text=="AirFiles":
					#Process each situation folder
					for situation in trainertype:
						#print("  "+situation.tag)
						#Get name
						elnameo=situation.findall("egc:name",ns)
						if len(elnameo)>0:
							sitname = elnameo[0].text
							print("Processing: "+sitname)
							#print("  "+icao)
							#List of aircraft in this situation
							#Todo: dict?
							aircraft=[]
							for pmark in situation:
								#print("    "+pmark.tag)
								#Get name
								elpmname=pmark.findall("egc:name",ns)
								if len(elpmname)>0:
									csign=elpmname[0].text
									elpts=pmark.findall("egc:Point",ns)
									#Get the coordinates
									if len(elpts)>0:
										for pt in elpts:
											elcoord=pt.findall("egc:coordinates",ns)
											#print("     "+coords)
											if len(elcoord)>0:
												coords=elcoord[0].text.strip().split(',')
												acdict['Lat']=coords[1]
												acdict['Lon']=coords[0]
												acdict['Alt']=coords[2]
												eldesc=pmark.findall("egc:description",ns)
												#Description holds a couple needed items
												if len(eldesc)>0:
													acdict=desctodict(eldesc[0].text)
													#Check for colon as it's not allowed in these fields
													invalid=0
													for field in acdict.values():
														bad = re.search(":",field)
														if bad:
															print("Found invalid character in: "+field)
															invalid=1
												# else: #Defaults
												#Maybe could figure out whether it's a departure or arrival
													# acdict=defaultac
													# closest=["ZZZZ",999]
													# for icao,coords in airportdict.items():
														# dist=cosinedist([acdict['Lat'],acdict['Lon']],airportdict[icao])
														# closest = [icao,dist] if dist<closest[1]
													# if closest[1]<3
													#print("     "+pt.tag)
													#Add to list as name and coords
													if not invalid:
														aircraft.append([csign,acdict])
														#print(parkings)
							#Write the airfile
							#Callsign:Type:Engine:Rules:Dep Field:Arr Field:Crz Alt:Route:Remarks:Sqk Code:Sqk Mode:Lat:Lon:Alt:Speed:Heading
							with open(sitname+".air","w") as sitfile:
								for callsign,acdict in aircraft:
									sitfile.write(callsign) #Start line with callsign
									#Each of the fields will start with the color separator
									for field in ["Type","Engine","Rules","Dep Field","Arr Field","Crz Alt","Route","Remarks","Sqk Code","Sqk Mode","Lat","Lon","Alt","Speed","Heading"]:
										sitfile.write(":"+acdict[field])
									sitfile.write("\n")

for t in tracons:
	ttapts[t[0]].writefile()
	eapts[t[0]].writefile()

satapts = {}
satapts['KPDX'] = ("KTTD", "KVUO")
satapts['KSEA'] = ("KBFI",)

for icao, ttapt in ttapts.items():
	if icao in satapts:
		for sat in satapts[icao]:
			ttapt.assimilate(ttapts[sat])
	#Write a file for this airport
	ttapt.writefile()

for icao, eapt in eapts.items():
	eapt.writefile()
