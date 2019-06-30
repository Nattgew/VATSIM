#!/usr/bin/env python3

import re
import random
import pickle
import MySQLdb
from enginetype import etype
from pathlib import Path
import math
import sys

#Callsign:Type:Engine:Rules:Dep Field:Arr Field:Crz Alt:Route:Remarks:Sqk Code:Sqk Mode:Lat:Lon:Alt:Speed:Heading

def makeairfile(fps, spots, felev, outfile):
    # Write a new air file with these values
    # Where to save the file
    # outfile = Path(r"")
    with open(outfile, "w") as airfile:
        for fp, spot in zip(fps, spots):
            print("Adding "+fp['callsign']+" to "+spot[0])
            # Get the line in the right syntax from the flight plan
            fpline = fptoline(fp, spot, felev)
            # Write the line to the file
            airfile.write(fpline+"\n")

def fptoline(fp, spot, felev):
    # Takes flight plan object and returns line for air file
    # Set the engine type
    try:
        # See if it's in our list
        engine = etype[fp['planned_aircraft']]
    except KeyError:
        # Assume it's a jet, what could go wrong
        print("Couldn't find engine type for "+fp['planned_aircraft']+", assuming jet")
        engine = "J"
    # TODO: find a better way to do this
    # Add main elements from flight plan
    lit = [fp['callsign'], fp['planned_aircraft'], engine, fp['planned_flighttype'], fp['planned_depairport'], fp['planned_destairport'], fp['planned_altitude'], fp['planned_route'], fp['planned_remarks']]
    # Read transponder, set random mode
    lit.extend([fp['transponder'],getrndmode()])
    # Coordinates of parking spot
    lit.extend([ str(i) for i in spot[1] ])
    # Field elevation
    lit.append(felev)
    # Speed and heading
    lit.extend(["0","360"])
    #print(lit)
    return ":".join(lit)

def getrndsq():
    # Gives a random squawk code
    sq = ""
    for i in range(4):
        sq += str(random.randint(0,7))
    return sq

def getrndmode():
    # Returns random squawk mode
    roll = random.randint(0,1)
    if roll:
        mode = "N"
    else:
        mode = "S"
    return mode

def getfplist(airport):
    print("Making mysql connection...")
    db = MySQLdb.connect(host="",    # your host, usually localhost
                         user="",         # your username
                         passwd="",  # your password
                         db="")        # name of the data base
    db.set_character_set('utf8')
    cur = db.cursor()
    cur.execute('SET NAMES utf8;')
    cur.execute('SET CHARACTER SET utf8;')
    cur.execute('SET character_set_connection=utf8;')

    keys = ["callsign", "cid", "realname", "clienttype", "frequency", "latitude", "longitude", "altitude", "groundspeed", "planned_aircraft", "planned_tascruise", "planned_depairport", "planned_altitude", "planned_destairport", "server", "protrevision", "rating", "transponder", "facilitytype", "visualrange", "planned_revision", "planned_flighttype", "planned_deptime", "planned_actdeptime", "planned_hrsenroute", "planned_minenroute", "planned_hrsfuel", "planned_minfuel", "planned_altairport", "planned_remarks", "planned_route", "planned_depairport_lat", "planned_depairport_lon", "planned_destairport_lat", "planned_destairport_lon", "atis_message", "time_last_atis_received", "time_logon", "heading", "QNH_iHg", "QNH_Mb"]
    flightplanlist = []

    print("Looking for matching rows at "+airport+"...")
    ret = cur.execute('SELECT * FROM flights WHERE planned_depairport = %s', (airport,))
    print("Found "+str(ret)+" rows:")
    for match in cur.fetchall():
    	#print(match)
    	client = {}
    	for key, val in zip(keys, match):
    		#print(key+" = "+str(val))
    		client[key] = str(val)
    	flightplanlist.append(client)
    return flightplanlist

def randomfp(airport):
    # Should return a random flight plan object
    fplist = getfplist(airport)
    return random.choice(fplist)

def manglealt(alt):
    # 1/3 chance to remove/add 1000 feet or do nothing
    newalt = str(int(alt)+1000*random.randint(-1,1))
    print("Mangled "+alt+" -> "+newalt)
    return newalt

def mangleroute(airport, route):
    # Chance of just swapping with another route
    chance_swap = 0.1
    # Chance of just filing DCT
    chance_dct = 0.1
    roll = random.randint(0,100)
    # Get a new route to use for shenanigans
    newplan = randomfp(airport)
    newroute = newplan['planned_route']
    if roll < chance_swap*100:
        # Already have the new route to use
        pass
    elif roll < (chance_swap+chance_dct)*100:
        newroute="DCT"
    else:
        # Split into lists
        origpoints = route.split(' ')
        newpoints = newroute.split(' ')
        # Choose how many of the first items to swap
        elemstoswap = random.randint(1,3)
        # Replace first X elements with those in other route
        origpoints[0:elemstoswap] = newpoints[0:elemstoswap]
        # Turn into one string again
        newroute = ' '.join(origpoints)
    print("Mangled "+route[:15]+"... -> "+newroute[:15]+"...")
    return newroute

def mangledest(dest):
    # Keep first letter, we'll go easy on 'em
    first = dest[:1]
    # Get a list of the remaining letters
    last = list(dest[1:])
    # Shuffle them around
    random.shuffle(last)
    # Put it back together
    shuffled = first + ''.join(last)
    print("Mangled "+dest+" -> "+shuffled)
    return shuffled

def rndeqpcode():
    # List of valid codes... we'll go easy on 'em
    validcodes = ['H','W','Z','L','X','T','U','D','B','A','M','N','P','Y','C','I','V','S','G']
    # 50/50 chance to just leave it blank
    isblank = random.randint(0,1)
    if isblank:
        thiscode = ""
    else:
        # Choose a random code
        thiscode = "/"+random.choice(validcodes)
    return thiscode

def splittype(type):
    fields = type.split('/')
    wt = ""
    ec = ""
    if len(fields[0]) == 1:
        wt = fields[0]
        type = fields[1]
        if len(fields) > 2:
            ec = fields[2]
    else:
        type = fields[0]
        if len(fields) > 1:
            ec = fields[1]

    return [wt, type, ec]

def mangleec(type):
    # Get item after last / in type field
    typefields = splittype(type)
    wt = typefields[0]
    newwt = wt
    if wt:
        if random.randint(0,1):
            if wt == "T":
                newwt = "H/"
            elif wt == "H":
                if random.randint(0,1):
                    newwt = ""
                else:
                    newwt = "T/"
    ec = typefields[2]
    newec = ec
    # If it's a single char, assume it's an eqp code
    if ec:
        # Replace with random code
        newec = rndeqpcode()
    newtype = newwt + typefields[1] + newec
    print("Mangled "+type+" -> "+newtype)
    type = newtype

    return type

def manglefp(fp):
    # Main function for introducing errors
    # Chance out of 1 for breaking each item
    chance_ec = 0.5
    chance_alt = 0.25
    chance_dest = 0.05
    chance_route = 0.25

    # Break items that meet a random roll
    if random.randint(0,100) < chance_ec*100:
        fp['planned_aircraft'] = mangleec(fp['planned_aircraft'])
    if random.randint(0,100) < chance_alt*100:
        fp['planned_altitude'] = manglealt(fp['planned_altitude'])
    if random.randint(0,100) < chance_dest*100:
        fp['planned_destairport'] = mangledest(fp['planned_destairport'])
    if random.randint(0,100) < chance_route*100:
        fp['planned_route'] = mangleroute(fp['planned_depairport'],fp['planned_route'])

    return fp

def cosinedist(latlon1,latlon2): #Use cosine to find distance between coordinates
    lat1, lon1 = latlon1
    lat2, lon2 = latlon2
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dellamb = math.radians(lon2-lon1)
    R = 3440.06479 # Nmi
    # gives d in Nmi
    d = math.acos( math.sin(phi1)*math.sin(phi2) + math.cos(phi1)*math.cos(phi2) * math.cos(dellamb) ) * R
    return int(round(d))

# Path to airport file for locations of parking spots
aptfilepath = Path(sys.argv[1])
outfile = Path(sys.argv[2])
# Holds list of spots
parkingspots=[]
fieldelev = 0

# Coordinates of airport to filter parking spots
# TODO: Look this up somehow
coords = [45.5887089,-122.5968694]

# Get list of parking spots to use
with open(aptfilepath, "r") as aptfile:
    name = ""
    for line in aptfile:
        line = line.strip()
        if name:
            # Last line was header, save the coordinates and name
            spotcoords = [ float(i) for i in line.split(' ') ]
            # Only keep if it's at this airport
            dist = cosinedist(coords, spotcoords)
            if dist < 3:
                parkingspots.append([name, spotcoords])
        if line[:9] == "[PARKING ":
            # Extract name from this line
            name = line[9:][:-1]
        else:
            # Not looking at a parking spot
            name = ""
            # See if this is field elevation
            if line[:16] == "field elevation=":
                # Save this to put new aircraft on ground
                fieldelev = line[16:]

# Randomize the order of parking spots
# Script will use them in order so hopefully we don't place them on top of each other
random.shuffle(parkingspots)
print(parkingspots)
parkingspots = iter(parkingspots)

# TODO: split into term, cargo, GA, and choose accordingly
gaspots = []
cargospots = []
otherspots = []
for spot in parkingspots:
    if re.search("GA", spot[0]) is not None:
        gaspots.append(spot)
    elif re.search("CARGO", spot[0]) is not None:
        cargospots.append(spot)
    else:
        otherspots.append(spot)

print("GA: "+str(len(gaspots))+"   CG: "+str(len(cargospots))+"   TR: "+str(len(otherspots)))
random.shuffle(gaspots)
random.shuffle(cargospots)
random.shuffle(otherspots)
gaspots = iter(gaspots)
cargospots = iter(cargospots)
otherspots = iter(otherspots)

cargoairlines = ["FDX","UPS","GEC","GTI","ATI","DHL","BOX","CLX","ABW","SQC","ABX","AEG","AJT","CLU","BDA","DAE","DHK","JOS","RTM","DHX","BCS","CKS","MPH","NCA","PAC","TAY","RCF","CAO","TPA","CKK","MSX","LCO","SHQ","LTG","ADB"]

gaaircraft = ["C172","C182","PC12","C208","PA28","BE35"]

# Get list of flight plans to use in random order
shuffledfps = getfplist("KPDX")
random.shuffle(shuffledfps)
flightplans = iter(shuffledfps)

while True:
    # Wait for input
    number = input("Press button, receive airplane...")
    if number:
        try:
            actoadd = int(number)
        except TypeError:
            actoadd = 1
    else:
        actoadd = 1
    # Loop through list of flight plans
    thesefps = []
    thesespots = []
    for i in range(actoadd):
        try:
            newfp = next(flightplans)
        except StopIteration:
            flightplans = iter(shuffledfps)
            newfp = next(flightplans)
        # Add errors to flight plan
        thesefps.append(manglefp(newfp))
        # Loop through parking spots
        airline = splittype(newfp['callsign'])[1]
        aircraft = splittype(newfp['planned_aircraft'])[1]
        if airline in cargoairlines:
            try:
                nextspot = next(cargospots)
            except StopIteration:
                cargospots = iter(cargospots)
                nextspot = next(cargospots)
        elif aircraft in gaaircraft:
            try:
                nextspot = next(gaspots)
            except StopIteration:
                gaspots = iter(gaspots)
                nextspot = next(gaspots)
        else:
            try:
                nextspot = next(otherspots)
            except StopIteration:
                otherspots = iter(otherspots)
                nextspot = next(otherspots)
        # try:
            # nextspot = next(parkingspots)
        # except StopIteration:
            # parkingspots = iter(parkingspots)
            # nextspot = next(parkingspots)
        thesespots.append(nextspot)
    # Save the file with aircraft in it
    makeairfile(thesefps, thesespots, fieldelev, outfile)
