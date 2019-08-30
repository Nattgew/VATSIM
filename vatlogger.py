#!/usr/bin/env python3

import re
import random
from pathlib import Path
import urllib.request
import os
import datetime
import MySQLdb

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
    if client['clienttype'] == "":
        client['clienttype'] = "PREFILE"
    return client

encoding = "utf-8"
# The status url provides lists of servers
statusurl = "http://status.vatsim.net/status.txt"
dataurls = []

with urllib.request.urlopen(statusurl) as response:
    html = response.read().decode(encoding, errors='replace')
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
            if clientsec:
                #print(line)
                clients.append(newclient(line))

db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="",         # your username
                     passwd="",  # your password
                     db="")        # name of the data base
db.set_character_set('utf8')
cur = db.cursor()
cur.execute('SET NAMES utf8;')
cur.execute('SET CHARACTER SET utf8;')
cur.execute('SET character_set_connection=utf8;')

keys = ["callsign", "cid", "realname", "clienttype", "frequency", "latitude", "longitude", "altitude", "groundspeed", "planned_aircraft", "planned_tascruise", "planned_depairport", "planned_altitude", "planned_destairport", "server", "protrevision", "rating", "transponder", "facilitytype", "visualrange", "planned_revision", "planned_flighttype", "planned_deptime", "planned_actdeptime", "planned_hrsenroute", "planned_minenroute", "planned_hrsfuel", "planned_minfuel", "planned_altairport", "planned_remarks", "planned_route", "planned_depairport_lat", "planned_depairport_lon", "planned_destairport_lat", "planned_destairport_lon", "atis_message", "time_last_atis_received", "time_logon", "heading", "QNH_iHg", "QNH_Mb"]

cur.execute('START TRANSACTION')
# Go through the current clients and find any we care about
for client in clients:
    if client['clienttype'] in ["PILOT","PREFILE"]:
        #print("Looking for cid: "+client['cid']+"   time: "+client['time_logon'])
        if client['clienttype'] == "PILOT":
            cur.execute('SELECT COUNT(*) FROM flights WHERE cid = %s AND time_logon = %s and planned_revision = %s', (client['cid'], client['time_logon'], client['planned_revision']))
        elif client['clienttype'] == "PREFILE":
            cur.execute('SELECT COUNT(*) FROM flights WHERE cid = %s AND planned_route = %s', (client['cid'], client['planned_route']))
        # print all the first cell of all the rows
        exist = cur.fetchone()[0]
        if not exist:
            row = []
            for key in keys:
                row.append(client[key])
#            print("Adding row len "+str(len(row))+":")
            #print(row)
            #print(tuple(client.values()))
            cur.execute('INSERT INTO flights VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', row)
        #else:
            #print("X")

db.commit()
db.close()
