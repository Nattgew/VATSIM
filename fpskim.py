#!/usr/bin/env python

import re
import pickle
import random
from pathlib import Path
import urllib.request
import os
import datetime

#http://status.vatsim.net/status.txt
#url0=http://data.vattastic.com/vatsim-data.txt
    #!CLIENTS:
    #callsign:cid:realname:clienttype:frequency:latitude:longitude:altitude:groundspeed:planned_aircraft:planned_tascruise:planned_depairport:planned_altitude:planned_destairport:server:protrevision:rating:transponder:facilitytype:visualrange:planned_revision:planned_flighttype:planned_deptime:planned_actdeptime:planned_hrsenroute:planned_minenroute:planned_hrsfuel:planned_minfuel:planned_altairport:planned_remarks:planned_route:planned_depairport_lat:planned_depairport_lon:planned_destairport_lat:planned_destairport_lon:atis_message:time_last_atis_received:time_logon:heading:QNH_iHg:QNH_Mb:

def newclient(line):
    client = {}
    keys = ["callsign", "cid", "realname", "clienttype", "frequency", "latitude", "longitude", "altitude", "groundspeed", "planned_aircraft", "planned_tascruise", "planned_depairport", "planned_altitude", "planned_destairport", "server", "protrevision", "rating", "transponder", "facilitytype", "visualrange", "planned_revision", "planned_flighttype", "planned_deptime", "planned_actdeptime", "planned_hrsenroute", "planned_minenroute", "planned_hrsfuel", "planned_minfuel", "planned_altairport", "planned_remarks", "planned_route", "planned_depairport_lat", "planned_depairport_lon", "planned_destairport_lat", "planned_destairport_lon", "atis_message", "time_last_atis_received", "time_logon", "heading", "QNH_iHg", "QNH_Mb"]
    elems = line.split(':')
    for key, val in zip(keys, elems):
        client[key] = val
    
    return client

timenow = datetime.datetime.now()
print(timenow)
# The status url provides lists of servers
statusurl = "http://status.vatsim.net/status.txt"
dataurls = []

with urllib.request.urlopen(statusurl) as response:
    html = response.read().decode("ansi")
    for line in html.split('\n'):
        #print(line)
        line = line.rstrip()
        # The url0 lines are places with full data files
        if line[:5] == "url0=":
            dataurls.append(line[5:])

# Pick one at random because they asked nicely
dataurl = random.choice(dataurls)
#dataurl = "http://data.vattastic.com/vatsim-data.txt"
# Local data file for testing
# datafile = Path(r"")

# We will add all clients to a list and then go through them
# We could filter them up front but this could be more flexible
clients = []

print("Using data url: "+dataurl)

with urllib.request.urlopen(dataurl) as response:
#with open(datafile, "r") as html:
    html = response.read().decode("ansi")
    #print(html)
    # Whether we are reading a section with clients to log
    clientsec = 0
    for line in html.split('\n'):
        #print(line)
        line = line.rstrip()
        # Like the universe, header sections begin with bang
        if line[:1] == "!":
            #print(line)
            # These are the sections we are looking for
            if line == "!CLIENTS:" or line == "!PREFILE:":
                #print(line)
                clientsec = 1
            else:
                clientsec = 0
        # If line is not empty or a comment
        elif line and line[:1] != ";":
            if clientsec:
                #print(line)
                clients.append(newclient(line))

# File for saving data locally
picklefile = Path(r"")
# Pull existing data from file
try:
	pdxdeps = pickle.load(open(picklefile, "rb"))
except FileNotFoundError:
    # No file, start with empty list
	#picklefile.touch()
	pdxdeps=[]

# Go through the current clients and find any we care about
for client in clients:
    if client['planned_depairport'] == "KPDX":
        print(client['callsign']+" "+client['planned_depairport']+"-"+client['planned_destairport'])
        # Check to make sure it isn't already stored
        # Maybe there's value in representing repeats, will evaluate later
        for logged in pdxdeps:
            # Test callsign and logon time, should be unique enough
            # This means if they disconnect/reconnect we'll log it again... probably fine
            if client['time_logon'] == logged['time_logon'] and client['callsign'] == logged['callsign']:
                print("Not logging dup")
                break
        else:
            # No dupes found, add to list
            pdxdeps.append(client)

# Save the list for next time
#print(pdxdeps)
pickle.dump(pdxdeps, open(picklefile, "wb"))
