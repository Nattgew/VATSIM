import xml.etree.ElementTree as ET

ns = {'egc': 'http://earth.google.com/kml/2.1'}
tree = ET.parse('example.kml')
root = tree.getroot()
runways=[]
parkings=[]
taxiways=[]
holds=[]
for document in root:
	print(document.tag)
	for airport in document:
		magvar=16
		fieldelev=20
		patternelev=1020
		patternsz=1
		initclbp=3000
		initclbj=5000
		jetairlines="AAL,ACA,AWE,BAW,BLR,BTA,CAL,CAX,COA,CVA,DAL"
		tpropairlines="EGF,USA,COA,CJC,JZA"
		reg="N"
		print("  "+airport.tag)
		elicao=airport.findall("egc:name",ns)
		if len(elicao)>0:
			icao = elicao[0].text
			print("  "+icao)
			for category in airport:
				print("   "+category.tag)
				elcategory=category.findall("egc:name",ns)
				if len(elcategory)>0:
					type=elcategory[0].text
					print("   "+type)
					if type=="Runways":
						for pmark in category:
							print("    "+pmark.tag)
							elpmname=pmark.findall("egc:name",ns)
							if len(elpmname)>0:
								pmname=elpmname[0].text
								ellin=pmark.findall("egc:LineString",ns)
								dthresh="500/0"
								turnoff="left"
								rwydict={}
								rwydict["name"]=pmname
								rwydict["dthresh"]=dthresh
								rwydict["turnoff"]=turnoff
								if len(ellin)>0:
									for line in ellin:
										print("     "+line.tag)
										elcoord=line.findall("egc:coordinates",ns)
										if len(elcoord)>0:
											rawcoordlist=[i.strip() for i in elcoord[0].text.strip().split(' ') if i!='']
											print("     coordlist")
											runways.append([rwydict,[rawcoordlist]])
					elif type=="Parking":
						for pmark in category:
							print("    "+pmark.tag)
							elpmname=pmark.findall("egc:name",ns)
							if len(elpmname)>0:
								pmname=elpmname[0].text
								elpts=pmark.findall("egc:Point",ns)
								if len(elpts)>0:
									for pt in elpts:
										print("     "+pt.tag)
										elcoord=pt.findall("egc:coordinates",ns)
										if len(elcoord)>0:
											coords=elcoord[0].text.strip()
											print("     "+coords)
											parkings.append([pmname,coords])
					elif type=="Taxiways":
						for pmark in category:
							print("    "+pmark.tag)
							elpmname=pmark.findall("egc:name",ns)
							if len(elpmname)>0:
								pmname=elpmname[0].text
								ellin=pmark.findall("egc:LineString",ns)
								if len(ellin)>0:
									for line in ellin:
										print("     "+line.tag)
										elcoord=line.findall("egc:coordinates",ns)
										if len(elcoord)>0:
											rawcoordlist=[i.strip() for i in elcoord[0].text.strip().split(' ') if i!='']
											print("     coordlist")
											taxiways.append([pmname,[rawcoordlist]])
					elif type=="Holds":
						for pmark in category:
							print("    "+pmark.tag)
							elpmname=pmark.findall("egc:name",ns)
							if len(elpmname)>0:
								pmname=elpmname[0].text
								elpts=pmark.findall("egc:Point",ns)
								if len(elpts)>0:
									for pt in elpts:
										print("     "+pt.tag)
										elcoord=pt.findall("egc:coordinates",ns)
										if len(elcoord)>0:
											coords=elcoord[0].text.strip()
											print("     "+coords)
											holds.append([pmname,coords])
					else:
						print("Did not recognize category: "+category)
			with open(icao+".apt","w") as airfile:
				print("icao="+icao)
				print("magnetic variation="+magvar)
				print("field elevation="+fieldelev)
				print("pattern elevation="+patternelev)
				print("pattern size="+patternsz)
				print("initial climb props="+initclbp)
				print("initial climb jets="+initclbj)
				print("jet airlines="+jetairlines)
				print("turboprop airlines="+tpropairlines)
				print("registration="+reg)
				print()

				for spot in parkings:
					print("[PARKING "+spot[0]+"]")
					print(spot[1][0]+" "+spot[1][1])
					print()

				for rwy in runways:
					print("[RUNWAY "+rwy[0]+"]")
					for node in rwy[1]:
						print(node[0]+" "+node[1])
					print()

				for twy in taxiways:
					print("[TAXIWAY "+twy[0]+"]")
					for node in twy[1]:
						print(node[0]+" "+node[1])
					print()

				for hold in holds:
					print("[HOLD "+hold[0]+"]")
					print(hold[1][0]+" "+hold[1][1])
