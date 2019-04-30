import xml.etree.ElementTree as ET
ns = {'egc': 'http://earth.google.com/kml/2.1'}
tree = ET.parse('example.kml')
root = tree.getroot()
apd={}
labels={}
for document in root:
	print(document.tag)
	for category in document:
		print(" "+category.tag)
		elcatname=category.findall("egc:name",ns)
		if len(elcatname)>0:
			catname=elcatname[0].text
			print(" "+catname)
			apd[catname]={}
			labels[catname]={}
		for airport in category:
			print("  "+airport.tag)
			elicao=airport.findall("egc:name",ns)
			if len(elicao)>0:
				icao = elicao[0].text
				print("  "+icao)
				apd[catname][icao]={}
				labels[catname][icao]={}
			for colorgroup in airport:
				print("   "+colorgroup.tag)
				elcolorname=colorgroup.findall("egc:name",ns)
				if len(elcolorname)>0:
					colorname=elcolorname[0].text
					print("   "+colorname)
					apd[catname][icao][colorname]=[]
					labels[catname][icao][colorname]=[]
				for pmark in colorgroup:
					print("    "+pmark.tag)
					elpmname=pmark.findall("egc:name",ns)
					if len(elpmname)>0:
						pmname=elpmname[0].text
					elpts=pmark.findall("egc:Point",ns)
					ellin=pmark.findall("egc:LineString",ns)
					if len(elpts)>0:
						for pt in elpts:
							print("     "+pt.tag)
							elcoord=pt.findall("egc:coordinates",ns)
							if len(elcoord)>0:
								coords=elcoord[0].text.strip()
								print("     "+coords)
								labels[catname][icao][colorname].append([pmname,coords])
					if len(ellin)>0:
						for line in ellin:
							print("     "+line.tag)
							elcoord=line.findall("egc:coordinates",ns)
							if len(elcoord)>0:
								rawcoordlist=[i.strip() for i in elcoord[0].text.strip().split(' ') if i!='']
								print("     coordlist")
								apd[catname][icao][colorname].append([rawcoordlist])
#print(apd)
#print(labels)
print("\n")
for category,icaos in apd.items():
	catpad=category.ljust(26)
	print(catpad+"N0000.000.000")
	for icao,colornames in icaos.items():
		print(";"+icao)
		for colorname,items in colornames.items():
			for item in items:
				for path in item:
					lastcoord=""
					for coord in path:
						#print(coord)
						if lastcoord!="":
							print(" "+lastcoord+" "+coord+" "+colorname)
						lastcoord=coord
						#print(item)
for category,icaos in labels.items():
	for icao,colornames in icaos.items():
		print(";"+icao+" - "+category)
		for colorname,items in colornames.items():
			for item in items:
				print('"'+item[0]+'" '+item[1]+" "+colorname)
