#!/usr/bin/env python

import re
import pickle

#http://status.vatsim.net/status.txt
#url0=http://data.vattastic.com/vatsim-data.txt
	#!CLIENTS:
	#callsign:cid:realname:clienttype:frequency:latitude:longitude:altitude:groundspeed:planned_aircraft:planned_tascruise:planned_depairport:planned_altitude:planned_destairport:server:protrevision:rating:transponder:facilitytype:visualrange:planned_revision:planned_flighttype:planned_deptime:planned_actdeptime:planned_hrsenroute:planned_minenroute:planned_hrsfuel:planned_minfuel:planned_altairport:planned_remarks:planned_route:planned_depairport_lat:planned_depairport_lon:planned_destairport_lat:planned_destairport_lon:atis_message:time_last_atis_received:time_logon:heading:QNH_iHg:QNH_Mb:

class client():
    def __init__(self, line):
        elems = line.split(':')
        callsign = elems[0]
        cid = elems[1]
        realname = elems[2]
        clienttype = elems[3]
        frequency = elems[4]
        latitude = elems[5]
        longitude = elems[6]
        altitude = elems[7]
        gspd = elems[8]
        plannedac = elems[9]
        plannedtas = elems[10]
        planneddep = elems[11]
        plannedalt = elems[12]
        planneddest = elems[13]
        server = elems[14]
        protrev = elems[15]
        rating = elems[16]
        xpdr = elems[17]
        fac = elems[18]
        visrng = elems[19]
        plrev = elems[20]
        planflttype = elems[21]
        plandeptime = elems[22]
        planactdeptime = elems[23]
        plannedhrs = elems[24]
        plannedmins = elems[25]
        plannedhrsfuel = elems[26]
        plannedminfuel = elems[27]
        plannedalt = elems[28]
        plannedrmk = elems[29]
        plannedroute = elems[30]
        #and so on...

dataurl = "http://data.vattastic.com/vatsim-data.txt"

clientsec = 0

clients = []

for line in datafile:
    if not clientsec:
        if line == "!CLIENTS:":
            clientsec = 1
    else:
        clients.append(client(line))

pdxdeps = pickle.load(open(picklefile, "rb"))
for client in clients:
    if client.planneddep == "KPDX":
        pdxdeps.append(client)

pickle.dump(pdxdeps, open(picklefile, "wb"))
