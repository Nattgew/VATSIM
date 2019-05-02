#!/usr/bin/env python

#Basic structure of sct2 file is as follows
#All headers listed, some not used here:
# ;header
# #define colors
# [REGIONS]
# [LABELS]
# [AIRPORT]
# [INFO]
# [VOR]
# [NDB]
# [RUNWAY]
# [FIXES]
# [ARTCC]
# [ARTCC HIGH] ;unused
# [ARTCC LOW] ;unused
# [SID]
# ========SIDs=========     N000.00.00.000 E000.00.00.000 N000.00.00.000 E000.00.00.000
# ========APDs=========     N000.00.00.000 E000.00.00.000 N000.00.00.000 E000.00.00.000
# (Airports)                 N000.00.00.000 E000.00.00.000 N000.00.00.000 E000.00.00.000
# ;KSEA...
# ======AIRSPACE=======     N000.00.00.000 E000.00.00.000 N000.00.00.000 E000.00.00.000
# =====VIDEO MAPS======     N000.00.00.000 E000.00.00.000 N000.00.00.000 E000.00.00.000
# [STAR]
# ========SUAs=========     N000.00.00.000 E000.00.00.000 N000.00.00.000 E000.00.00.000
# =====VIDEO MAPS======     N000.00.00.000 E000.00.00.000 N000.00.00.000 E000.00.00.000
# **COMMON DATA**            N000.00.00.000 E000.00.00.000 N000.00.00.000 E000.00.00.000 ; GEO stuff
# ==SECTOR BOUNDARIES==     N000.00.00.000 E000.00.00.000 N000.00.00.000 E000.00.00.000
# ===2 SECTOR SPLIT===         N000.00.00.000 E000.00.00.000 N000.00.00.000 E000.00.00.000
# [LOW AIRWAY]
# [HIGH AIRWAY]
# [GEO] ;unused

import re, math

def cosinedist(coord1,coord2): #Use cosine to find distance between coordinates
	lat1,lon1 = coord1
	lat2,lon2 = coord2
	phi1 = math.radians(lat1)
	phi2 = math.radians(lat2)
	dellamb = math.radians(lon2-lon1)
	R = 3440.06479 # Nmi
	# gives d in Nmi
	d = math.acos( math.sin(phi1)*math.sin(phi2) + math.cos(phi1)*math.cos(phi2) * math.cos(dellamb) ) * R
	return d

def dmstodd(clist):
	#["N000.00.00.000","E000.00.00.000"]
	#Get the letters
	latletter=clist[0][:1]
	lonletter=clist[1][:1]
	#Start with positive/negative based on letters
	declat=1 if latletter=="N" else -1
	declon=1 if lonletter=="E" else -1
	#print(clist)
	#Split by decimals, exclude leading letters
	latelems=clist[0][1:].split('.')
	lonelems=clist[1][1:].split('.')
	#print(latelems)
	#print(lonelems)
	#Calculate decimal degrees
	#Multiply by itself which was set above as positive/negative by letter
	declat*=int(latelems[0])+int(latelems[1])/60+float(latelems[2]+"."+latelems[3])/3600
	declon*=int(lonelems[0])+int(lonelems[1])/60+float(lonelems[2]+"."+lonelems[3])/3600
	return [declat,declon]

#Sectorfiles to be updated
#Filename to be sectorile_airac.sct2
sectorfiles=[
	"BLI_TWR_V1",
	"EUG_APP_PRO_V1",
	"GEG_APP_PRO_V1",
	"LMT_APP_PRO_V1",
	"MFR_APP_PRO_V1_1",
	"MWH_APP_PRO_V1",
	"OTH_TWR_V1",
	"P80_TRACON_PRO_V1_2",
	"PSC_APP_PRO_V1",
	"S46-PRO-v2_2",
	"YKM_APP_PRO_V1_1",
	"ZSE-v3_05"
]

#List of main airports and which sector they are in
airportsector={
	"KSEA":"S46",
	"KPDX":"P80"
}

#Current airac cycle, part of filenames
airac="1903"

#Iterate over each sectorfile
#Basic workflow is:
# Read current sector file and split into sections
# Write new file, inserting new content as required
#for sfile in sectorfiles:
	#Name of sector is first three characters of filename
	#sectorname=sfile[:3]
sfile="ZSE-v3_05"
sectorname="ZSE"

#These are the sections we are looking for
#These are the only ones VRC recognizes
#Each section will be a string to hold the applicable lines
#Initialized as blank so we can append
#The keys are lower case of the actual titles
#Code will search the upper case version in brackets to identify it
#Anything unrecognized will get added to previous section
#Sections will be written in the new file in the order listed here
#Nonexistent sections will simply add nothing to new file
sections={}
for key in ["header","colors","info","regions","low airway","high airway","airport","vor","ndb","runway","fixes","artcc","sid","star","labels","artcc high","artcc low","geo"]:
	sections[key]=""
#This will hold the subsections in SID and STAR sections
#We don't care about most of them (for now) but need to put new diagrams in the right spot
subsecs={"sid":{},"star":{}}

#Every ICAO key will correspond to coordinates from the AIRPORT section
#This is used to exclude existing labels for airports that have new labels defined
airports={}

#This will come from the KML reader to exclude existing labels near these fields
allnewdiagrams=["KSEA"]
if sectorname=="ZSE":
	#ZSE will include everything
	newairports=allnewdiagrams
else:
	#Only pick out new airports in this sector
	newairports=[]
	for newdiag in allnewdiagrams:
		if airportsector[newdiag]==sectorname:
			newairports.append(newdiag)

#Start with the header section of comments
currsec="header"
subsec=""
currfile=sfile+"_"+airac+".sct2"
f=open(r+currfile,'r')
for line in f:
	#Build the airport coordinates dictionary
	if currsec=="airport": #do this first so we skip the header line
		#WY67 000.000 N041.47.21.809 W110.32.30.609
		#Split by spaces, remove blanks/newline
		elems=[i for i in line.strip().split(' ') if i!='']
		#print(elems)
		#0 for empty line, 1 for next header
		#Could test only for >3 but would like to investigate if it's in between
		if len(elems)>1:
			#Convert to decimal degrees
			dcoords=dmstodd([elems[2],elems[3]])
			#Add airport and coords to dict
			airports[elems[0]]=dcoords
	#See if we've made it to the colors section
	#Maybe could be combined with headers
	if re.search("^#define",line) is not None:
		currsec="colors"
	#Otherwise we're in the thick of it, see if we're starting a new section
	elif currsec!="headers":
		for key in sections.keys():
			#see if the line is [SECTION]
			if re.search("^\["+key.upper()+"\]",line) is not None:
				currsec=key
				#If we just switched from SID to STAR, we need to blank this out until we get the next one
				subsec="" 
				break
	#Break SID and STAR down into subsections
	#TODO: Search for actual headers, not just ( and =
	if currsec in ["sid","star"]:
		#Search for the headers in parens
		reparen = re.search("^(\(.+\))",line)
		#Search for the headers in equals
		reeq = re.search("^=+([^=]+)=+",line)
		#If either of these matches, start a new section
		if reparen is not None:
			subsec=reparen[1] #Get name of subsection
			print("New subsec: "+subsec)
			subsecs[currsec][subsec]=line #Add the header line to it
		elif reeq is not None:
			subsec=reeq[1]
			print("New subsec: "+subsec)
			subsecs[currsec][subsec]=line
		# for key,sub in subsecs.items():		
			# print(sub)
		elif subsec!="": #if no new section but we are in one
			#print("Adding to "+currsec+" -> "+subsec)
			subsecs[currsec][subsec]+=line
		sections[currsec]+=line #write to the main list too
	else: #Any other random line
		subsec="" #Just in case
		sections[currsec]+=line

#Don't keep labels around airports we have new labels for
#String to hold the lines we keep
keptlines=""
#Print out the names and locations of airports to prune, mostly for debug
for newapt in newairports:
	coords=airports[newapt]
	print("Will prune for %s: %f,%f" % (newapt,coords[0],coords[1]))
#Actually prune all labels lines
for line in sections["labels"].split('\n'):
	# reicao=re.search("^;.+K[A-Z0-9]{3}",line)
	# if reicao is not None:
		# print("Found airport labels for: "+line)
	#See if line looks like a label
	relbl=re.search('^".+" +[NS]',line)
	if relbl is not None:
		#print("Found label: "+line)
		#Split by spaces and remove spaces/newline
		lblelems=[i for i in line.strip().split(' ') if i!='']
		#Convert coords to decimal
		lblcoords=dmstodd([lblelems[1],lblelems[2]])
		#Check against new airports
		prune=0
		for newapt in newairports:
			#Calculate distance of label from airport
			dist=cosinedist(airports[newapt],lblcoords)
			#Prune if distance less than theshold
			#3 seems to just exclude our closest cases while accounding for large fields
			#Could possibly be smaller
			#Another way to do this would be to draw exclusion zones around each airport like X-Plane does
			if dist<3:
				prune=1
				break
			# if dist<8:
				# print(dist)
		# if prune:
			# print("Pruning for "+newapt+":"+line)
		if not prune:
			keptlines+=line #Keep anything not pruned

#Rewrite labels section to just be the lines we kept
sections["labels"]="[LABELS]\n"+keptlines
		#print(lblcoords)
#print(sections["header"])
#print(airports)

#Write each main section to its own file, mostly for debug
for key in sections.keys():
	with open(key+".txt","w") as partfile:
		partfile.write(sections[key])

newfile=sfile+"_"+airac+"-NEW.sct2"
#Build new sector file
with open(newfile,"w") as newsct:
	#Write each section
	for key,contents in sections.items():
		#Handle special cases first
		if key=="colors":
			#print("Writing: "+key)
			#Write existing colors
			newsct.write(contents)
			#Write new colors
			newsct.write("#define FANTASTIC COLORS GO HERE\n\n\n")
		elif key=="sid":
			#Need to insert new diagrams
			#Write header first
			newsct.write("[SID]\n")
			#Go through the subsections
			for subkey,subcon in subsecs["sid"].items():
				#New stuff goes right before airspace
				#Could do this as being right after (Airports) too
				if subkey=="AIRSPACE":
					newsct.write("(Current Airport Diagrams) N000.00.00.000 E000.00.00.000 N000.00.00.000 E000.00.00.000\n\n")
					newsct.write("(Old Diagram REF)          N000.00.00.000 E000.00.00.000 N000.00.00.000 E000.00.00.000\n\n")
				#print("Writing sub: "+subkey)
				newsct.write(subcon)
		else: #Business as usual
			print("Writing: "+key)
			newsct.write(contents)

#Needs to be cleaned up, not all filenames work
# for key in subsecs.keys():
	# with open(key+".txt","w") as partfile:
		# partfile.write(subsecs[key])

#for key,sub in subsecs.items():		
#	print(sub.keys())
