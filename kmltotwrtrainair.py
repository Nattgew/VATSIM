#!/usr/bin/env python
import xml.etree.ElementTree as ET

ns = {'egc': 'http://www.opengis.net/kml/2.2'}
tree = ET.parse('TowerTrainer.kml')
root = tree.getroot()
for document in root:
	#print(document.tag)
	for docitem in document:
		#print(" "+docitem.tag)
#		if docitem.tag=="egc:Folder":
		elnameo=docitem.findall("egc:name",ns)
		#if len(elnameo)>0:
			#print(elnameo[0].text)
		if len(elnameo)>0 and elnameo[0].text=="TowerTrainer":
			for trainertype in docitem:
				#print("  "+trainertype.tag)
				elnameo=trainertype.findall("egc:name",ns)
				if len(elnameo)>0 and elnameo[0].text=="AirportFiles":
					for airport in trainertype:
						eldesc=airport.findall("egc:description",ns)
						descdict={}
						if len(eldesc)>0:
							lines = eldesc[0].text.split('\n')
							#print(lines)
							for line in lines:
								#print(line)
								assign = line.split('=')
								descdict[assign[0]]=assign[1]
							try:
								magvar=descdict["magnetic variation"]
								fieldelev=descdict["field elevation"]
								patternelev=descdict["pattern elevation"]
								patternsz=descdict["pattern size"]
								initclbp=descdict["initial climb props"]
								initclbj=descdict["initial climb jets"]
								jetairlines=descdict["jet airlines"]
								tpropairlines=descdict["turboprop airlines"]
								reg=descdict["registration"]
							except:
								magvar="16"
								fieldelev="20"
								patternelev="1020"
								patternsz="1"
								initclbp="3000"
								initclbj="5000"
								jetairlines="AAL,ACA,AWE,BAW,BLR,BTA,CAL,CAX,COA,CVA,DAL"
								tpropairlines="EGF,USA,COA,CJC,JZA"
								reg="N"
						else:
							magvar="16"
							fieldelev="20"
							patternelev="1020"
							patternsz="1"
							initclbp="3000"
							initclbj="5000"
							jetairlines="AAL,ACA,AWE,BAW,BLR,BTA,CAL,CAX,COA,CVA,DAL"
							tpropairlines="EGF,USA,COA,CJC,JZA"
							reg="N"
						#print("  "+airport.tag)
						elicao=airport.findall("egc:name",ns)
						if len(elicao)>0:
							icao = elicao[0].text
							print("Processing: "+icao)
							#print("  "+icao)
							runways=[]
							parkings=[]
							taxiways=[]
							holds=[]
							for category in airport:
								#print("   "+category.tag)
								elcategory=category.findall("egc:name",ns)
								if len(elcategory)>0:
									type=elcategory[0].text
									#print("   "+type)
									if type=="runway":
										for pmark in category:
											#print("    "+pmark.tag)
											elpmname=pmark.findall("egc:name",ns)
											if len(elpmname)>0:
												pmname=elpmname[0].text
												eldesc=pmark.findall("egc:description",ns)
												ellin=pmark.findall("egc:LineString",ns)
												descdict={}
												if len(eldesc)>0:
													lines = eldesc[0].text.split('\n')
													#print(lines)
													for line in lines:
														#print(line)
														assign = line.split('=')
														descdict[assign[0]]=assign[1]
													dthresh = descdict["displaced threshold"]
													turnoff = descdict["turnoff"]
												else:
													dthresh="500/0"
													turnoff="left"
												rwydict={}
												rwydict["name"]=pmname
												rwydict["dthresh"]=dthresh
												rwydict["turnoff"]=turnoff
												if len(ellin)>0:
													for line in ellin:
														#print("     "+line.tag)
														elcoord=line.findall("egc:coordinates",ns)
														if len(elcoord)>0:
															rawcoordlist=[[i.strip().split(',')[1],i.strip().split(',')[0]] for i in elcoord[0].text.strip().split(' ') if i!='']
															#print(rawcoordlist)
															#print("     coordlist")
															runways.append([rwydict,rawcoordlist])
									elif type=="parking":
										for pmark in category:
											#print("    "+pmark.tag)
											elpmname=pmark.findall("egc:name",ns)
											if len(elpmname)>0:
												pmname=elpmname[0].text
												elpts=pmark.findall("egc:Point",ns)
												if len(elpts)>0:
													for pt in elpts:
														#print("     "+pt.tag)
														elcoord=pt.findall("egc:coordinates",ns)
														if len(elcoord)>0:
															coords=elcoord[0].text.strip().split(',')
															latlon=[coords[1],coords[0]]
															#print("     "+coords)
															parkings.append([pmname,latlon])
															#print(parkings)
									elif type=="taxiway":
										for pmark in category:
											#print("    "+pmark.tag)
											elpmname=pmark.findall("egc:name",ns)
											if len(elpmname)>0:
												pmname=elpmname[0].text
												ellin=pmark.findall("egc:LineString",ns)
												if len(ellin)>0:
													for line in ellin:
														#print("     "+line.tag)
														elcoord=line.findall("egc:coordinates",ns)
														if len(elcoord)>0:
															rawcoordlist=[[i.strip().split(',')[1],i.strip().split(',')[0]] for i in elcoord[0].text.strip().split(' ') if i!='']
															#print(rawcoordlist)
															#print("     coordlist")
															taxiways.append([pmname,rawcoordlist])
									elif type=="hold":
										for pmark in category:
											#print("    "+pmark.tag)
											elpmname=pmark.findall("egc:name",ns)
											if len(elpmname)>0:
												pmname=elpmname[0].text
												elpts=pmark.findall("egc:Point",ns)
												if len(elpts)>0:
													for pt in elpts:
														#print("     "+pt.tag)
														elcoord=pt.findall("egc:coordinates",ns)
														if len(elcoord)>0:
															coords=elcoord[0].text.strip().split(',')
															latlon=[coords[1],coords[0]]
															#print("     "+coords)
															holds.append([pmname,latlon])
									else:
										print("Did not recognize category: "+type)
							with open(icao+".apt","w") as airfile:
								airfile.write("icao="+icao+"\n")
								airfile.write("magnetic variation="+magvar+"\n")
								airfile.write("field elevation="+fieldelev+"\n")
								airfile.write("pattern elevation="+patternelev+"\n")
								airfile.write("pattern size="+patternsz+"\n")
								airfile.write("initial climb props="+initclbp+"\n")
								airfile.write("initial climb jets="+initclbj+"\n")
								airfile.write("jet airlines="+jetairlines+"\n")
								airfile.write("turboprop airlines="+tpropairlines+"\n")
								airfile.write("registration="+reg+"\n\n")

								for spot in parkings:
									airfile.write("[PARKING "+spot[0]+"]\n")
									airfile.write(spot[1][0]+" "+spot[1][1]+"\n\n")

								for rwy in runways:
									airfile.write("[RUNWAY "+rwy[0]['name']+"]\n")
									airfile.write("displaced threshold="+rwy[0]['dthresh']+"\n")
									airfile.write("turnoff="+rwy[0]['turnoff']+"\n")
									for node in rwy[1]:
										airfile.write(node[0]+" "+node[1]+"\n")
									airfile.write("\n")

								for twy in taxiways:
									airfile.write("[TAXIWAY "+twy[0]+"]\n")
									#print(twy[1])
									for node in twy[1]:
										airfile.write(node[0]+" "+node[1]+"\n")
									airfile.write("\n")

								for hold in holds:
									airfile.write("[HOLD "+hold[0]+"]\n")
									airfile.write(hold[1][0]+" "+hold[1][1]+"\n\n")
