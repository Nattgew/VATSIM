#!/usr/bin/env python3

#import re
import random
from pathlib import Path
import urllib.request
import os
import pickle
import MySQLdb
import sys

#http://status.vatsim.net/status.txt
#url0=http://data.vattastic.com/vatsim-data.txt
    #!CLIENTS:
    #callsign:cid:realname:clienttype:frequency:latitude:longitude:altitude:groundspeed:
    # planned_aircraft:planned_tascruise:planned_depairport:planned_altitude:planned_destairport:
    # server:protrevision:rating:transponder:facilitytype:visualrange:
    # planned_revision:planned_flighttype:planned_deptime:planned_actdeptime:
    # planned_hrsenroute:planned_minenroute:planned_hrsfuel:planned_minfuel:
    # planned_altairport:planned_remarks:planned_route:
    # planned_depairport_lat:planned_depairport_lon:planned_destairport_lat:planned_destairport_lon:
    # atis_message:time_last_atis_received:time_logon:heading:QNH_iHg:QNH_Mb:

    # rating:
    # 1 - OBS
    # 2 - S1
    # 3 - S2
    # 4 - S3
    # 5 - C1
    # 8 - I1

    # facilitytype:
    # 1 - OBS
    # 2 - DEL
    # 3 - GND
    # 4 - TWR
    # 5 - APP
    # 6 - CTR


# class airport():
#
#     def __init__(self, icao, lat, lon):
#         self.icao = icao
#         self.lat = lat
#         self.lon = lon


def newclient(line):
    client = {}
    keys = ["callsign", "cid", "realname", "clienttype", "frequency", "latitude", "longitude", "altitude", "groundspeed", "planned_aircraft", "planned_tascruise", "planned_depairport", "planned_altitude", "planned_destairport", "server", "protrevision", "rating", "transponder", "facilitytype", "visualrange", "planned_revision", "planned_flighttype", "planned_deptime", "planned_actdeptime", "planned_hrsenroute", "planned_minenroute", "planned_hrsfuel", "planned_minfuel", "planned_altairport", "planned_remarks", "planned_route", "planned_depairport_lat", "planned_depairport_lon", "planned_destairport_lat", "planned_destairport_lon", "atis_message", "time_last_atis_received", "time_logon", "heading", "QNH_iHg", "QNH_Mb"]
    elems = line.split(':')
    # Create dict using the key list
    for key, val in zip(keys, elems):
        # Set blanks to null
        if val == "":
            val = None
        client[key] = val
    if client['clienttype'] == "":
        client['clienttype'] = "PREFILE"
    return client

encoding = "utf-8"
# The status url provides lists of servers
statusurl = "http://status.vatsim.net/status.txt"
statusfile = Path("/home/pi/vatstatus.pickle")


try:
    dataurls = pickle.load(open(statusfile, "rb"))
    print("Got server list from file")
except FileNotFoundError:
    # No file, start with empty list
    print("Getting new server list")
    dataurls = []
    # Get status page to find list of servers
    with urllib.request.urlopen(statusurl) as response:
        html = response.read().decode(encoding, errors='replace')
        for line in html.split('\n'):
            #print(line)
            line = line.rstrip()
            # The url0 lines are places with full data files
            if line[:5] == "url0=":
                dataurls.append(line[5:])

# Save server list for next time
pickle.dump(dataurls, open(statusfile, "wb"))

# Pick one at random because they asked nicely
dataurl = random.choice(dataurls)
#dataurl = "http://data.vattastic.com/vatsim-data.txt"
# Local data file for testing
# datafile = Path(sys.argv[1])

# We will add all clients to a list and then go through them
# We could filter them up front but this could be more flexible
clients = []

# TODO: catch exceptions on this and try next url, etc.
print("Using data url: "+dataurl)
#print("Reading file...")
with urllib.request.urlopen(dataurl) as response:
#with open(datafile, "r") as html:
    html = response.read().decode(encoding, errors='replace')
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
            # Parse the client in the list
            if clientsec:
                #print(line)
                clients.append(newclient(line))
#print("Processing clients from "+sys.argv[1]+"...")
db = MySQLdb.connect(host="localhost",
                     user="",
                     passwd="",
                     db="")
db.set_character_set('utf8')
cur = db.cursor()
cur.execute('SET NAMES utf8;')
cur.execute('SET CHARACTER SET utf8;')
cur.execute('SET character_set_connection=utf8;')

keys = ["callsign", "cid", "realname", "frequency", "latitude", "longitude", "altitude", "groundspeed", "planned_aircraft", "planned_tascruise", "planned_depairport", "planned_altitude", "planned_destairport", "server", "rating", "transponder", "facilitytype", "visualrange", "planned_revision", "planned_flighttype", "planned_deptime", "planned_actdeptime", "planned_hrsenroute", "planned_minenroute", "planned_hrsfuel", "planned_minfuel", "planned_altairport", "planned_remarks", "planned_route", "time_logon", "heading", "QNH_iHg", "QNH_Mb"]

cur.execute('START TRANSACTION')
# Go through the current clients and find any we care about
for client in clients:
    if client['clienttype'] in ["PILOT","PREFILE"]:
        row = []
        # Build the main row list
        for key in keys:
            row.append(client[key])
        if client['clienttype'] == "PILOT":
            cur.execute('INSERT INTO flights SELECT %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s FROM DUAL WHERE NOT EXISTS (SELECT * FROM flights WHERE cid = %s AND time_logon = %s and planned_revision = %s LIMIT 1)', (*row, client['cid'], client['time_logon'], client['planned_revision']))
        elif client['clienttype'] == "PREFILE":
            cur.execute('INSERT INTO flights SELECT %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s FROM DUAL WHERE NOT EXISTS (SELECT * FROM flights WHERE cid = %s AND planned_route = %s LIMIT 1)', (*row, client['cid'], client['planned_route']))
            
        # Improvement on previous code?
        # if client['clienttype'] == "PILOT":
            # sql = 'SELECT EXISTS(SELECT 1 FROM flights WHERE cid = %s AND time_logon = %s and planned_revision = %s LIMIT 1)'
            # val = (client['cid'], client['time_logon'], client['planned_revision'])
        # elif client['clienttype'] == "PREFILE":
            # sql = 'SELECT EXISTS(SELECT 1 FROM flights WHERE cid = %s AND planned_route = %s LIMIT 1)'
            # val = (client['cid'], client['planned_route'])
        # if not cur.execute(sql, val):

# Another way to do it, insert all rows at end
#cur.executemany('INSERT INTO flights VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', rows)
#print("Committing new of "+str(pi)+" pilots, "+str(pr)+" prefile from "+sys.argv[1]+"...")
db.commit()
db.close()
