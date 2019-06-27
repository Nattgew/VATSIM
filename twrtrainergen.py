#!/usr/bin/env python

import re
import random
from pathlib import Path

#Callsign:Type:Engine:Rules:Dep Field:Arr Field:Crz Alt:Route:Remarks:Sqk Code:Sqk Mode:Lat:Lon:Alt:Speed:Heading

class flightplan():
	def __init__(self, cs, tp, rl, dp, ar, alt, rt, rmk):
		callsign = cs
		type = tp
		engine = "j"
		rules = rl
		orig = dp
		dest = ar
		altitude = alt
		route = rt
		remarks = rmk

def makeairfile(fp, spot, felev):
	# Write a new air file with these values
	# Where to save the file
	outfile = Path("")
	print("Adding "+fp.callsign+" to "+spot[0])
	with open outfile as airfile:
		fpline = fptoline(fp, spot, felev)
		airfile.write(fpline)

def fptoline(fp, spot, felev):
	# Takes flight plan object and returns line for air file
	lit = [ i for i in fp.__dict__.values ]
	lit.extend([getrndsq(),getrndmode()])
	lit.extend(spot[1])
	lit.append(felev)
	lit.extend(["0","360"])

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
	else
		mode = "S"
	
	return mode

def getfp():
	# Should return a random flight plan object
	return None

def manglealt(alt):
	# 1/3 chance to remove/add 1000 feet or do nothing
	return alt+1000*random.randint(-1,1)

def mangleroute(route):
	# Chance of just swapping with another route
	chance_swap = 0.1
	# Chance of just filing DCT
	chance_dct = 0.1
	roll = random.randint(0,100)
	# Get a new route to use for shenanigans
	newplan = getfp()
	newroute = newplan.route
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

def mangleec(type)
	# Get item after last / in type field
	ec = type.split('/')[-1:][0]
	# If it's a single char, assume it's an eqp code
	if len(ec) == 1:
		# Replace with random code
		newec = rndeqpcode()
		type = type[:-2]+newec
	
	return type

def manglefp(fp):
	# Chance out of 1 for breaking each item
	chance_ec = 0.5
	chance_alt = 0.25
	chance_dest = 0.05
	chance_route = 0.25
	
	roll = randint(0,100)
	
	# Break items that met the random roll
	if roll < chance_ec*100:
		fp.type = mangleec(fp.type)
	if roll < chance_alt*100:
		fp.altitude = manglealt(fp.altitude)
	if roll < chance_dest*100:
		fp.dest = mangledest(fp.dest)
	if roll < chance_route*100:
		fp.route = mangleroute(fp.route)
	
	return fp


# Path to airport file for locations of parking spots
aptfilepath = Path(r"")
# Holds list of spots
parkingspots=[]
fieldelev = 0

with open aptfilepath as aptfile:
	for line in aptfile:
		if name:
			# Last line was header, save the coordinates and name
			parkingspots.append(['name',line.strip().split(' ')])
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

# Track which spot to use next
nextspotindex = 0

while true:
	# Wait for input
	input("Press button, receive airplane...")
	newfp = getfp()
	enhancedfp = manglefp(newfp)
	makeairfile(enhancedfp, parkingspots[nextspotindex], fieldelev)
	nextspotindex += 1
