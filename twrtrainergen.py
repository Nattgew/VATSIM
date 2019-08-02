#!/usr/bin/env python3

import re
import random
import MySQLdb
import pickle
import sqlite3
from enginetype import etype
from pathlib import Path
import math
import sys
from tkinter import Tk
import os


def makeairfile(acs, felev, outfile):
    # Write a new air file with these values
    # outfile = Path(r"")
    with open(outfile, "w") as airfile:
        for ac in acs:
            print("Adding "+ac[0]['callsign']+" to "+ac[1][0])
            # Get the line in the right syntax from the flight plan
            fpline = fptoline(ac, felev)
            # Write the line to the file
            airfile.write(fpline+"\n")


def fptoline(ac, felev):
    # Takes flight plan object and returns line for air file
    # Callsign:Type:Engine:Rules:Dep Field:Arr Field:Crz Alt:Route:Remarks:Sqk Code:Sqk Mode:Lat:Lon:Alt:Speed:Heading
    # Set the engine type
    type = splittype(ac[0]['planned_aircraft'])[1]
    try:
        # See if it's in our list
        engine = etype[type.upper()]
    except KeyError:
        # Assume it's a jet, what could go wrong
        print("Couldn't find engine type for "+type+", assuming jet")
        engine = "J"
    # TODO: find a better way to do this
    # Add main elements from flight plan
    lit = [ac[0]['callsign'], ac[0]['planned_aircraft'], engine, ac[0]['planned_flighttype'], ac[0]['planned_depairport'], ac[0]['planned_destairport'], ac[0]['planned_altitude'], ac[0]['planned_route'], ac[0]['planned_remarks']]
    # Read transponder, set random mode
    xpdr = ac[0]['transponder']
    if xpdr == "0":
        xpdr = getrndsq()
    lit.extend([xpdr, getrndmode()])
    # Coordinates of parking spot
    lit.extend([str(i) for i in ac[1][1]])
    # Field elevation
    lit.append(felev)
    # Speed and heading
    lit.extend(["0", "360"])
    # print(lit)
    # Print out a string for each flight plan's main details
    string = "%s | %s | %s -> %s | %s | %s" % (ac[0]['callsign'], ac[0]['planned_aircraft'], ac[0]['planned_depairport'], ac[0]['planned_destairport'], ac[0]['planned_altitude'], ac[0]['planned_route'])
    print(string)
    # Automatically copy to clipboard
    addtoclipboard(string)
    return ":".join(lit)


def addtoclipboard(string):
    # r = Tk()
    # r.withdraw()
    # r.clipboard_clear()
    # r.clipboard_append(string)
    # r.update()
    # r.destroy()
    command = 'echo "' + string.strip() + '" | clip'
    os.system(command)


def getrndsq():
    # Gives a random squawk code (string)
    print("Generating random squawk...")
    sq = ""
    # Avoid special codes... for now
    while sq in ["", "7500", "7600", "7700"]:
        for i in range(4):
            sq += str(random.randint(0, 7))
    return sq


def getrndmode():
    # Returns random squawk mode
    mode = "N" if random.randint(0, 1) else "S"
    return mode


def getfplist(airport):
    # Return a list of flight plans from this airport
    # First need to get the database cursor
    conn = getdbconn_mysql()
    cur = conn.cursor()
    cur.execute('SHOW COLUMNS FROM flights')
    keys = [i[0] for i in cur.fetchall()]
    flightplanlist = []
    # print("Looking for matching rows at "+airport+"...")
    ret = cur.execute('SELECT * FROM flights WHERE planned_depairport = %s', (airport,))
    # print("Found "+str(ret)+" rows:")
    for match in cur.fetchall():
        # print(match)
        client = {}
        for key, val in zip(keys, match):
            # print(key+" = "+str(val))
            client[key] = str(val)
        flightplanlist.append(client)
    conn.close()
    return flightplanlist


def getfplist_pickle(airport):
    # Location of file with flight plans
    fpfile = Path(r"")
    flightplanlist = pickle.load(open(fpfile, "rb"))
    return flightplanlist


def getdbconn_sqlite():
    # Return database cursor for sqlite file
    fpfile = Path(r"")
    conn = sqlite3.connect(fpfile)
    # c = conn.cursor()
    return conn


def getdbconn_mysql():
    # Return database cursor for mysql server
    # print("Making mysql connection...")
    db = MySQLdb.connect(host="",    # your host, usually localhost
                         user="",         # your username
                         passwd="",  # your password
                         db="")        # name of the data base
    db.set_character_set('utf8')
    cur = db.cursor()
    cur.execute('SET NAMES utf8;')
    cur.execute('SET CHARACTER SET utf8;')
    cur.execute('SET character_set_connection=utf8;')
    return db


def randomfp(airport):
    # Should return a random flight plan object
    fplist = getfplist(airport)
    return random.choice(fplist)


def manglealt(alt):
    # Catch cases with letters, change to int for calc
    if alt[:2] == "FL":
        newalt = int(alt[2:])*100
    elif alt[:1] == "F":
        newalt = int(alt[1:])*100
    else:
        newalt = int(alt)
    # 1/3 chance to remove/add 1000 feet or do nothing
    newalt = str(newalt+1000*random.randint(-1, 1))
    print("Mangled "+alt+" -> "+newalt)
    return newalt


def mangleroute(airport, route):
    # Chance of swapping entire route
    chance_swap = 0.1
    # Chance of just filing DCT
    chance_dct = 0.05
    # Chance of blank route
    chance_blk = 0.05
    # Otherwise swap just part of the route
    # Get a new route to use for shenanigans
    newplan = randomfp(airport)
    newroute = newplan['planned_route']
    if random.randint(0, 100) < chance_swap*100:
        # Already have the new route to use
        pass
    elif random.randint(0, 100) < chance_dct*100:
        newroute = "DCT"
    elif random.randint(0, 100) < chance_blk*100:
        newroute = ""
    else:
        # Just swap first few points
        # Split into lists
        origpoints = re.split(' |\.', route)
        newpoints = re.split(' |\.', newroute)
        # Choose how many of the first items to swap
        elemstoswap = random.randint(1, 4)
        # Replace first X elements with those in other route
        origpoints[:elemstoswap] = newpoints[:elemstoswap]
        # Turn into one string again
        newroute = ' '.join(origpoints)
    print("Mangled "+route[:25]+"... -> "+newroute[:25]+"...")
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
    thiscode = "" if random.randint(1, 10) > 1 else "/"+random.choice(validcodes)
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
        if random.randint(0, 1):
            if wt == "T":
                # print("Changing T to H")
                newwt = "H/"
            elif wt == "H":
                # If it's H, 50/50 either remove or change to T
                newwt = "" if random.randint(0, 1) else "T/"
        else:
            # Don't mess with it
            newwt = wt+"/"
    else:
        # No weight, 50/50 we add something
        if random.randint(0, 1):
            # 50/50 choice of T or H
            newwt = "T/" if random.randint(0, 1) else "H/"
    # ec = typefields[2]
    # If it's a single char, assume it's an eqp code
    # Replace with random code
    newec = rndeqpcode()
    newtype = newwt + typefields[1] + newec
    print("Mangled "+type+" -> "+newtype)

    return newtype


def manglefp(fp, focus=None):
    # Main function for introducing errors
    # Chance out of 1 for breaking each item
    if focus == "TWR":
        # If focus on TWR, rely on pilots to provide the errors
        chance_ec = 0.01
        chance_alt = 0.01
        chance_dest = 0.001
        chance_route = 0.01
    else:
        # If focus is on GND, add errors to enhance training
        chance_ec = 0.5
        chance_alt = 0.25
        chance_dest = 0.01
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


def getlocations(fp):
    # Return list of coordinates where this client was seen stationary
    # print("Getting locations for this client...")
    conn = getdbconn_mysql()
    cur = conn.cursor()
    ret = cur.execute('SELECT latitude, longitude FROM flights WHERE callsign = %s AND time_logon = %s AND groundspeed = "0"', (fp['callsign'], fp['time_logon']))
    print("Found "+str(ret)+" total coordinates for "+fp['callsign'])
    coords = []
    for loc in cur.fetchall():
        # print(loc)
        coords.append([float(j) for j in loc])
    conn.close()
    return coords


def usespot(fp, spots):
    # Attempt to use nearest spot to airplane's location
    spotmatch = ""
    coords = getlocations(fp)
    # Don't match if they're moving
    # if fp['groundspeed'] == "0":
    for loc in coords:
        dists = []
        # Calculate distance to all spots
        for spot in spots:
            # print("Finding dist...")
            dists.append((spot, cosinedist(loc, spot[1])))
        # print(dists)
        # Sort the list by the distances
        dsort = sorted(dists, key=lambda dist: dist[1])
        # print(dsort)
        # If closest spot is within tolerance, return that spot
        if dsort[0][1] < 200/6076:
            print("Matching original spot "+dsort[0][0][0])
            spotmatch = dsort[0][0]
            break
        else:
            print("Closest spot "+dsort[0][0][0]+" was "+str(round(dsort[0][1]*6076))+"ft away")
    # else:
        # print("GS "+fp['groundspeed']+" > 0")

    return spotmatch


def cosinedist(latlon1, latlon2):  # Use cosine to find distance between coordinates
    lat1, lon1 = latlon1
    lat2, lon2 = latlon2
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dellamb = math.radians(lon2-lon1)
    R = 3440.06479  # Nmi
    # gives d in Nmi
    d = math.acos(math.sin(phi1)*math.sin(phi2) + math.cos(phi1)*math.cos(phi2) * math.cos(dellamb)) * R
    return d


def loopiter(theiter):
    # Return next item and keep looping through this list
    # Using lists instead of iter so it's easy to move things around as needed
    # try:
        # newit = next(theiter)
    # except StopIteration:
        # # If we run out, start from beginning
        # # print("Recycling list...")
        # theiter = iter(shuffled)
        # newit = next(theiter)
    # Return first item, move it to the end
    nextspot = theiter[0]
    theiter.remove(nextspot)
    theiter.append(nextspot)
    return theiter, nextspot


# Path to airport file for locations of parking spots
aptfilepath = Path(sys.argv[1])
outfile = Path(sys.argv[2])
# Holds list of spots
parkingspots = []
fieldelev = 0

# Coordinates of airport to filter parking spots
# TODO: Look this up somehow
aptcoords = {'KPDX': [45.5887089, -122.5968694],
             'KSEA': [47.4498889, -122.3117778]
             }

# Get list of parking spots to use
with open(aptfilepath, "r") as aptfile:
    name = ""
    for line in aptfile:
        line = line.strip()
        definition = line.split("=")
        # See if this is a field we care about
        if definition[0] == "field elevation":
            # Save this to put new aircraft on ground
            fieldelev = definition[1]
        elif definition[0] == "icao":
            # Save this to know what airport we're at
            airport = definition[1]
            coords = aptcoords[airport]
        if name:
            # Last line was header, save the coordinates and name
            spotcoords = [float(i) for i in line.split(' ')]
            # Only keep if it's at this airport
            dist = cosinedist(coords, spotcoords)
            if dist < 3:
                parkingspots.append([name, spotcoords])
        if line[:9] == "[PARKING ":
            # Extract name from this line
            name = line[9:-1]
        else:
            # Not looking at a parking spot
            name = ""

if len(parkingspots) == 0:
    raise RuntimeError("Didn't find any parking spots!")
# Randomize the order of parking spots
# Script will use them in order so hopefully we don't place them on top of each other
random.shuffle(parkingspots)

# Allow splitting into term, cargo, GA, and choose accordingly
gaspots = []
cargospots = []
milspots = []
otherspots = []
# Try to identify spots based on name
for spot in parkingspots:
    if re.search("GA", spot[0]) is not None:
        gaspots.append(spot)
    elif re.search("CARGO", spot[0]) is not None:
        cargospots.append(spot)
    elif re.search("ANG", spot[0]) is not None:
        milspots.append(spot)
    else:
        otherspots.append(spot)
print("GA: "+str(len(gaspots))+"   CG: "+str(len(cargospots))+"   MI: "+str(len(milspots))+"   TR: "+str(len(otherspots)))

# Shuffle and create iterables
random.shuffle(gaspots)
random.shuffle(cargospots)
random.shuffle(milspots)
random.shuffle(otherspots)

# Keep track of recently used spots
usedspots = []

# Airlines to put on cargo ramps
cargoairlines = ["FDX", "UPS", "GEC", "GTI", "ATI", "DHL", "BOX", "CLX", "ABW", "SQC", "ABX", "AEG", "AJT", "CLU", "BDA", "DAE", "DHK", "JOS", "RTM", "DHX", "BCS", "CKS", "MPH", "NCA", "PAC", "TAY", "RCF", "CAO", "TPA", "CKK", "MSX", "LCO", "SHQ", "LTG", "ADB"]

# For aircraft not listed, would rather have GA at term than airliner at GA
gaaircraft = ["C172", "C182", "PC12", "C208", "PA28", "BE35", "B350", "FA20", "C750", "CL30", "C25", "BE58", "BE9L", "HAWK", "C150", "P06T", "H25B", "TBM7", "P28U", "BE33", "AC11", "DHC6", "EA50", "SF50", "C510", "M7", "DC3", "UH1", "E55P", "TBM9", "PC21", "C25A", "B58T", "H850", "BE20", "DA42", "S76", "Z50", "A139", "C206", "AC50", "EPIC", "LJ45", "LJ60", "C404", "FA50", "C170", "GLF5", "C210", "FA7X", "DA62", "DR40", "P28A", "KODI", "SR22", "SR20", "P28B", "C550", "B36T", "DHC3", "DHC2", "GLEX", "B60T", "PC7", "E50P", "DA40", "AS50", "PA24", "C152", "ULAC", "BE30", "S550", "E300", "PA22", "J3", "B24", "B25", "B29", "B17", "PC6T", "T210", "BE36", "BE56", "P28R", "F406", "T51", "ST75", "CL60", "GL5T", "LJ24", "LJ25", "LJ31", "LJ40", "LJ55", "LJ75", "P38", "L10", "L12", "L29B", "L29A", "L14", "P2", "L37", "F2TH", "F900", "MYS4", "FA10", "DA50", "DJET", "PA25", "E200", "E230", "E400", "E500", "AS32", "AS3B", "AS55", "AS65", "EC45", "EC20", "EC30", "EC35", "EC55", "EC25", "TIGR", "BK17", "B412", "B06", "B205", "B212", "B222", "B230", "B407", "B427", "B430", "B47G", "A109", "A119", "A129", "B06T", "C421", "BE60", "TBM8", "PA31", "D401", "C500", "PA18", "R22", "R44", "C525", "PAY1", "PAY2", "PA30", "PRM1", "R66", "AEST", "EH10", "PA11", "BE18", "SIRA", "PA32", "M20P", "M20J", "C441", "B609", "LEG2", "BT36", "YK40", "TOBA", "BE55", "PZ04", "WT9", "L39", "C310", "PA20", "C56X", "E550", "CL35", "P180", "BE40", "YK18", "M20T", "PV1", "SH36", "P51", "T6", "SPIT", "C207", "PA28R", "A5", "PA34", "CHIN", "GL7T", "S92", "COL4", "PA46", "B462", "P46T", "LANC", "RV8", "G21", "AC68", "B429", "BN2P", "LJ35", "PA27", "TRIN", "UNIV", "AC90", "C402", "AN12", "HA4T", "MI8", "AN2", "GIV", "GLF4", "GLF2", "GLF6", "A210", "CAT", "CDC6", "PA38", "DO28", "GA5C", "B461", "B18T", "P28S", "C46", "EXPL", "B200", "DH2T", "AS21", "C68A", "PAY4", "B463", "PC24", "SLG2", "ASTO", "SP6", "SP7", "P166", "P66P", "P66T", "S360", "DC3T", "C77R", "E545", "FA5X", "G400", "S22T", "ECHO", "MJ5", "AC14", "C414", "MU2", "PA44", "SREY", "EFOX", "C185", "PAY3", "G115", "M200", "TB20", "P28T", "GLID", "P111", "SF25", "VW10", "P32R", "AP28", "DHC4", "A22", "PRPR", "D8", "DH3T", "BE99", "PA47", "AA5", "BDOG", "DV20", "A33"]

# Try to put mil aircraft at mil spots
milaircraft = ["F35", "T38", "F15", "F14", "F22", "F18", "A10", "F4", "C130", "B52", "B1", "B2", "CV22", "MV22", "V22", "H60", "CH47", "CH55", "C5", "C17", "C141", "EA6B", "A6", "P8", "P3", "P3C", "E3", "E3CF", "E3TF", "C97", "E6", "K35A", "K35E", "K35R", "KE3", "R135", "HAR", "E2", "C2", "B58", "EUFI", "SU11", "SU15", "SU17", "SU20", "SU22", "SU24", "SU25", "SU35", "SU30", "SU32", "SU34", "SU27", "MG29", "MG31", "E767", "U2", "SR71", "A4", "RQ1", "MQ9", "CH60", "H64", "H46", "H47", "H66", "F104", "F117", "VF35", "S3", "T33", "A7", "F8", "MIR2", "MIRA", "MIR4", "MRF1", "RFAL", "ETAR", "SMB2", "AJET", "F106", "F101", "MG21", "A400", "F18H", "VULC", "SUCO", "A50", "H53", "V35B", "C30J", "MH60", "TEX2", "F35A", "CNBR", "T160", "V10", "TOR", "AN22", "F5", "UH1Y", "AN32", "CN35", "AN26"]

# Get list of flight plans to use in random order
# Only add unique callsigns, otherwise random could add dupes
# First get list from this airport
shuffledfps = getfplist(airport)
if len(shuffledfps) == 0:
    raise RuntimeError('No flight plans found!')
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
print("Found "+str(len(shuffledfps))+" plans and "+str(len(filteredfps))+" callsigns")

# Keep running until killed
while True:
    # Keep list of used spots to a reasonable 
    if len(usedspots)>14:
        usedspots = usedspots[1:]
    # Wait for input
    number = input("\nPress button, receive airplane...")
    # If we get a valid number as input, add that many airplanes
    if number:
        try:
            actoadd = int(number)
        except (TypeError, ValueError):
            actoadd = 1
    else:
        # If we don't recognize number input, just add one
        actoadd = 1
    # List of aircraft and spots in this batch
    theseacs = []
    # Create as many aircraft as were requested
    for i in range(actoadd):
        try:
            newfp = next(flightplans)
        except StopIteration:
            # If we run out, start from beginning
            flightplans = iter(shuffledfps)
            newfp = next(flightplans)
        # Add errors to flight plan
        nextfp = manglefp(newfp)
        # Try to use original spot
        nextspot = usespot(newfp, parkingspots)
        if nextspot:
            # Further attention if we found a matching spot
            # Could go with next nearest spot but that could jump to another list
            # TODO: loop through nearest spots in matching list?
            # See if it's been recently used
            if nextspot in usedspots:
                print("Too recent, picking from top")
                # Find which list it's in and use the next spot in that list
                for thislist in [cargospots, gaspots, milspots, otherspots]:
                    if nextspot in thislist:
                        thislist, nextspot = loopiter(thislist)
            else:
                # Not too recently used, move this spot to end of its list
                print("Moving "+nextspot[0]+" to end of list")
                for thislist in [cargospots, gaspots, milspots, otherspots]:
                    if nextspot in thislist:
                        thislist.remove(nextspot)
                        thislist.append(nextspot)
            # for thislist in [cargospots, gaspots, milspots, otherspots]:
                # print([i[0] for i in thislist])
        else:
            print("Using random spot")
            # Pull first three chars for airline name
            airline = newfp['callsign'][:3]
            aircraft = splittype(newfp['planned_aircraft'])[1].strip()
            # Loop through parking spots
            if airline in cargoairlines and cargospots:
                cargospots, nextspot = loopiter(cargospots)
            elif aircraft in gaaircraft and gaspots:
                gaspots, nextspot = loopiter(gaspots)
            elif aircraft in milaircraft and milspots:
                milspots, nextspot = loopiter(milspots)
            else:
                otherspots, nextspot = loopiter(otherspots)
            # try:
                # nextspot = next(parkingspots)
            # except StopIteration:
                # parkingspots = iter(parkingspots)
                # nextspot = next(parkingspots)
        # Add the spot to the list of recently used
        usedspots.append(nextspot)
        # Add to list of aircraft in this batch
        theseacs.append((nextfp, nextspot))
    # Save the file with aircraft in it
    makeairfile(theseacs, fieldelev, outfile)
