#!/usr/bin/env python3

import re
import random
import MySQLdb
from enginetype import etype
from pathlib import Path
import math
import sys

# Callsign:Type:Engine:Rules:Dep Field:Arr Field:Crz Alt:Route:Remarks:Sqk Code:Sqk Mode:Lat:Lon:Alt:Speed:Heading


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
    type = splittype(fp['planned_aircraft'])[1]
    try:
        # See if it's in our list
        engine = etype[type]
    except KeyError:
        # Assume it's a jet, what could go wrong
        print("Couldn't find engine type for "+type+", assuming jet")
        engine = "J"
    # TODO: find a better way to do this
    # Add main elements from flight plan
    lit = [fp['callsign'], fp['planned_aircraft'], engine, fp['planned_flighttype'], fp['planned_depairport'], fp['planned_destairport'], fp['planned_altitude'], fp['planned_route'], fp['planned_remarks']]
    # Read transponder, set random mode
    lit.extend([fp['transponder'], getrndmode()])
    # Coordinates of parking spot
    lit.extend([str(i) for i in spot[1]])
    # Field elevation
    lit.append(felev)
    # Speed and heading
    lit.extend(["0", "360"])
    # print(lit)
    return ":".join(lit)


def getrndsq():
    # Gives a random squawk code
    sq = ""
    for i in range(4):
        sq += str(random.randint(0, 7))
    return sq


def getrndmode():
    # Returns random squawk mode
    roll = random.randint(0, 1)
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
        # print(match)
        client = {}
        for key, val in zip(keys, match):
            # print(key+" = "+str(val))
            client[key] = str(val)
        flightplanlist.append(client)
    return flightplanlist


def randomfp(airport):
    # Should return a random flight plan object
    fplist = getfplist(airport)
    return random.choice(fplist)


def manglealt(alt):
    # Catch cases with letters
    if alt[:2] == "FL":
        alt = int(alt[2:])*100
    elif alt[:1] == "F":
        alt = int(alt[1:])*100
    # 1/3 chance to remove/add 1000 feet or do nothing
    newalt = str(int(alt)+1000*random.randint(-1, 1))
    print("Mangled "+alt+" -> "+newalt)
    return newalt


def mangleroute(airport, route):
    # Chance of swapping entire route
    chance_swap = 0.1
    # Chance of just filing DCT
    chance_dct = 0.1
    # Get a new route to use for shenanigans
    newplan = randomfp(airport)
    newroute = newplan['planned_route']
    if random.randint(0, 100) < chance_swap*100:
        # Already have the new route to use
        pass
    elif random.randint(0, 100) < chance_dct*100:
        newroute = "DCT"
    else:
        # Just swap first few points
        # Split into lists
        origpoints = route.split(' ')
        newpoints = newroute.split(' ')
        # Choose how many of the first items to swap
        elemstoswap = random.randint(1, 3)
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
    validcodes = ['H', 'W', 'Z', 'L', 'X', 'T', 'U', 'D', 'B', 'A', 'M', 'N', 'P', 'Y', 'C', 'I', 'V', 'S', 'G']
    # 50/50 chance to just leave it blank
    isblank = random.randint(0, 1)
    if isblank:
        thiscode = ""
    else:
        # Choose a random code
        thiscode = "/"+random.choice(validcodes)
    return thiscode


def splittype(type):
    # Splits type by / into weight, type, and eqp codes
    # Anything not there returns a blank
    fields = type.split('/')
    # print("Split "+type+" -> "+str(fields))
    # Blank by default
    wt = ""
    ec = ""
    if len(fields[0]) == 1:
        # Assume first field must be weight, followed by type
        if len(fields) > 1:
            wt = fields[0]
            type = fields[1]
            if len(fields) > 2:
                # If there's another field, must be eqp code
                ec = fields[2]
        else:
            type = fields[0]
    else:
        # Assume first field must be type
        type = fields[0]
        if len(fields) > 1:
            # If there's anothe field, must be eqp code
            ec = fields[1]
    return [wt, type, ec]


def mangleec(type):
    # Get item after last / in type field
    typefields = splittype(type)
    wt = typefields[0]
    newwt = wt
    if wt:
        # If there's a weight, 50/50 we mess with it
        # print("Fount wt")
        if random.randint(0, 1):
            if wt == "T":
                # print("Changing T to H")
                newwt = "H/"
            elif wt == "H":
                # If it's H, 50/50 either remove or change to T
                if random.randint(0, 1):
                    # print("Changing H to none")
                    newwt = ""
                else:
                    # print("Changing H to T")
                    newwt = "T/"
        else:
            # Don't mess with it
            newwt = wt+"/"
    else:
        # No weight, 50/50 we add something
        if random.randint(0, 1):
            # 50/50 choice of T or H
            if random.randint(0, 1):
                newwt = "T/"
            else:
                newwt = "H/"
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
    if random.randint(0, 100) < chance_ec*100:
        fp['planned_aircraft'] = mangleec(fp['planned_aircraft'])
    if random.randint(0, 100) < chance_alt*100:
        fp['planned_altitude'] = manglealt(fp['planned_altitude'])
    if random.randint(0, 100) < chance_dest*100:
        fp['planned_destairport'] = mangledest(fp['planned_destairport'])
    if random.randint(0, 100) < chance_route*100:
        fp['planned_route'] = mangleroute(fp['planned_depairport'], fp['planned_route'])

    return fp


def cosinedist(latlon1, latlon2):  # Use cosine to find distance between coordinates
    lat1, lon1 = latlon1
    lat2, lon2 = latlon2
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dellamb = math.radians(lon2-lon1)
    R = 3440.06479  # Nmi
    # gives d in Nmi
    d = math.acos(math.sin(phi1)*math.sin(phi2) + math.cos(phi1)*math.cos(phi2) * math.cos(dellamb)) * R
    return int(round(d))


def loopiter(theiter, shuffled):
    try:
        newit = next(theiter)
    except StopIteration:
        # If we run out, start from beginning
        theiter = iter(shuffled)
        newit = next(theiter)
    return newit


# Path to airport file for locations of parking spots
aptfilepath = Path(sys.argv[1])
outfile = Path(sys.argv[2])
# Holds list of spots
parkingspots = []
fieldelev = 0

# Coordinates of airport to filter parking spots
# TODO: Look this up somehow
coords = [45.5887089, -122.5968694]

# Get list of parking spots to use
with open(aptfilepath, "r") as aptfile:
    name = ""
    for line in aptfile:
        line = line.strip()
        if name:
            # Last line was header, save the coordinates and name
            spotcoords = [float(i) for i in line.split(' ')]
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
            definition = line.split("=")
            # See if this is a field we care about
            if definition[0] == "field elevation":
                # Save this to put new aircraft on ground
                fieldelev = definition[1]
            elif definition[0] == "icao":
                # Save this to know what airport we're at
                airport = definition[1]

# Randomize the order of parking spots
# Script will use them in order so hopefully we don't place them on top of each other
random.shuffle(parkingspots)
print(parkingspots)
parkingspots = iter(parkingspots)

# Allow splitting into term, cargo, GA, and choose accordingly
gaspotshuff = []
cargospotshuff = []
milspotshuff = []
otherspotshuff = []
# Try to identify spots based on name
for spot in parkingspots:
    if re.search("GA", spot[0]) is not None:
        gaspotshuff.append(spot)
    elif re.search("CARGO", spot[0]) is not None:
        cargospotshuff.append(spot)
    elif re.search("ANG", spot[0]) is not None:
        milspotshuff.append(spot)
    else:
        otherspotshuff.append(spot)
print("GA: "+str(len(gaspotshuff))+"   CG: "+str(len(cargospotshuff))+"   MI: "+str(len(milspotshuff))+"   TR: "+str(len(otherspotshuff)))

# Shuffle and create iterables
random.shuffle(gaspotshuff)
random.shuffle(cargospotshuff)
random.shuffle(milspotshuff)
random.shuffle(otherspotshuff)
gaspots = iter(gaspotshuff)
cargospots = iter(cargospotshuff)
milspots = iter(milspotshuff)
otherspots = iter(otherspotshuff)

# Airlines to put on cargo ramps
cargoairlines = ["FDX", "UPS", "GEC", "GTI", "ATI", "DHL", "BOX", "CLX", "ABW", "SQC", "ABX", "AEG", "AJT", "CLU", "BDA", "DAE", "DHK", "JOS", "RTM", "DHX", "BCS", "CKS", "MPH", "NCA", "PAC", "TAY", "RCF", "CAO", "TPA", "CKK", "MSX", "LCO", "SHQ", "LTG", "ADB"]

# For aircraft not listed, would rather have GA at term than airliner at GA
gaaircraft = ["C172", "C182", "PC12", "C208", "PA28", "BE35", "B350", "FA20", "C750", "CL30", "C25", "BE58", "BE9L", "HAWK", "C150", "P06T", "H25B", "TBM7", "P28U", "BE33", "AC11", "DHC6", "EA50", "SF50", "C510", "M7", "DC3", "UH1", "E55P", "TBM9", "PC21", "C25A", "B58T", "H850", "BE20", "DA42", "S76", "Z50", "A139", "C206", "AC50", "EPIC", "LJ45", "LJ60", "C404", "FA50", "C170", "GLF5", "C210", "FA7X", "DA62", "DR40", "P28A", "KODI", "SR22", "SR20", "P28B", "C550", "B36T", "DHC3", "DHC2", "GLEX", "B60T", "PC7", "E50P", "DA40", "AS50", "PA24", "C152", "ULAC", "BE30", "S550", "E300", "PA22", "J3", "B24", "B25", "B29", "B17", "PC6T", "T210", "BE36", "BE56", "P28R", "F406", "T51", "ST75", "CL60", "GL5T", "LJ24", "LJ25", "LJ31", "LJ40", "LJ55", "LJ75", "P38", "L10", "L12", "L29B", "L29A", "L14", "P2", "L37", "F2TH", "F900", "MYS4", "FA10", "DA50", "DJET", "PA25", "E200", "E230", "E400", "E500", "AS32", "AS3B", "AS55", "AS65", "EC45", "EC20", "EC30", "EC35", "EC55", "EC25", "TIGR", "BK17", "B412", "B06", "B205", "B212", "B222", "B230", "B407", "B427", "B430", "B47G", "A109", "A119", "A129", "B06T", "C421", "BE60", "TBM8", "PA31", "D401"]

# Try to put mil aircraft at mil spots, if avail
milaircraft = ["F35", "T38", "F15", "F14", "F22", "F18", "A10", "F4", "C130", "B52", "B1", "B2", "CV22", "MV22", "V22", "H60", "CH47", "CH55", "C5", "C17", "C141", "EA6B", "A6", "P8", "P3", "P3C", "E3", "E3CF", "E3TF", "C97", "E6", "K35A", "K35E", "K35R", "KE3", "R135", "HAR", "E2", "C2", "B58", "EUFI", "SU11", "SU15", "SU17", "SU20", "SU22", "SU24", "SU25", "SU35", "SU30", "SU32", "SU34", "SU27", "MG29", "MG31", "E767", "U2", "SR71", "A4", "RQ1", "MQ9", "CH60", "H64", "H46", "H47", "H66", "F104", "F117", "VF35", "S3", "T33", "A7", "F8", "MIR2", "MIRA", "MIR4", "MRF1", "RFAL", "ETAR", "SMB2", "AJET", "F106", "F101", "MG21"]

# Get list of flight plans to use in random order
# Only add unique callsigns, otherwise random could add dupes
# First get list from this airport
shuffledfps = getfplist(airport)
# Shuffle them
random.shuffle(shuffledfps)
# Get a list of unique callsigns
uniquecallsigns = list(set([i['callsign'] for i in shuffledfps]))
filteredfps = []
for fp in shuffledfps:
    if fp['callsign'] in uniquecallsigns:
        # If it's still in the list of callsigns, add to our filtered list
        filteredfps.append(fp)
        # Remove from the list of uniques so no more plans get added for that callsign
        uniquecallsigns.remove(fp['callsign'])
flightplans = iter(filteredfps)

while True:
    # Wait for input
    number = input("\nPress button, receive airplane...")
    # If we get a valid number as input, add that many airplanes
    if number:
        try:
            actoadd = int(number)
        except (TypeError, ValueError):
            actoadd = 1
    else:
        # If we don't recognize it, just add one
        actoadd = 1
    # Loop through list of flight plans
    thesefps = []
    thesespots = []
    for i in range(actoadd):
        try:
            newfp = next(flightplans)
        except StopIteration:
            # If we run out, start from beginning
            flightplans = iter(shuffledfps)
            newfp = next(flightplans)
        # Add errors to flight plan
        thesefps.append(manglefp(newfp))
        # Pull first three chars for airline name
        airline = newfp['callsign'][:3]
        aircraft = splittype(newfp['planned_aircraft'])[1]
        # Loop through parking spots
        if airline in cargoairlines and cargospots:
            nextspot = loopiter(cargospots, cargospotshuff)
        elif aircraft in gaaircraft and gaspots:
            nextspot = loopiter(gaspots, gaspotshuff)
        elif aircraft in milaircraft and milspots:
            nextspot = loopiter(milspots, milspotshuff)
        else:
            nextspot = loopiter(otherspots, otherspotshuff)
        # try:
            # nextspot = next(parkingspots)
        # except StopIteration:
            # parkingspots = iter(parkingspots)
            # nextspot = next(parkingspots)
        thesespots.append(nextspot)
    # Save the file with aircraft in it
    makeairfile(thesefps, thesespots, fieldelev, outfile)
