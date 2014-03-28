#!/usr/bin/env python
"""
	GPS.PY
    v.2

	written by: Manuel Dionne
	credit to: the internet
"""

import sys
import subprocess
import time
import urllib2
from decimal import *
from subprocess import *

baud = '60'
mark_freq = '20300'
space_freq = '20250'
confidence = '0.4'
calc_factor = Decimal(0.250)
getcontext().prec = 6

"""
function parse packet

returns the time and pos in a GPS packet that looks like this:
START|TIME|POS|IDENTIFIER|END

returns: float time, list position, int identifier
"""
def internet_on():
    try:
        response=urllib2.urlopen('http://74.125.228.100',timeout=1)
        return True
    except urllib2.URLError as err: pass
    return False


def parse_packet(packet):
    #Check if it's one of our packets
    if packet[0:6] == "START|":
        #parse the time
        time = ""
        i = 7
        for i in range(6,100):
            if not packet[i] == "|":
                time = time + packet[i]
                continue
            posstart = i
            break
        #parse the position
        pos = ""
        i = posstart + 1
        for i in range(posstart + 1,100):
            if not packet[i] == "|":
                pos = pos + packet[i]
                continue
            posend = i
            break
        #split the pos string and put it in a list
        i = 0
        identifier = "N/A"
        finalpos = []
        for i in range(0,len(pos)):
            if pos[i] == "_":
                finalpos.append(pos[0:i])
                x = posend + 1
                for x in range(posend,len(packet)):
                    if packet[x:len(packet)] == "1|END":
                        identifier = 1
                    if packet[x:len(packet)] == "2|END":
                        identifier = 2
                finalpos.append(pos[i+1:posend])

        #return the time and list
	data = []
	data.append(Decimal(time))
	data.append(finalpos)
	data.append(identifier)
        return data

minimodem = subprocess.Popen(["minimodem","--rx","-8","-q",baud,'--space',space_freq,'--mark',mark_freq,'-c',confidence], stdout=subprocess.PIPE)

def main():
	print 'starting'
        refreshtime = 29
        oldpacketstart = Decimal(0)
	while True:
            c = minimodem.stdout.read(1)
            print ">>> Got first char: ", c
            if not c == "|":
                continue
            packetstart = Decimal("%.6f" % time.time())
            print ">>> Packet start time:", packetstart
    	    line = minimodem.stdout.readline()[0:51]
    	    if not line:
    		break
    	    print ">>> " + line.rstrip()
            pp = parse_packet(line)
            if pp is None:
                print ">>> not a packet/broken packet"
                continue
            data =  list(pp)
            print ">>> PACKET: ", data
	    print ">>> ------------------------------------------------------------"
            print ">>> TIME OF DEPARTURE: ", data[0]
            print ">>> TIME OF ARRIVAL: ", oldpacketstart
            traveltime = oldpacketstart - data[0]
            print ">>> TRAVEL TIME: ", traveltime
            dist = (traveltime - Decimal(0.4)) * Decimal(300)
            print ">>> DISTANCE: ", dist
            print ">>> POS: ", data[1]
            print ">>> IDEN: ", data[2]
            print ">>> ------------------------------------------------------------"
            oldpacketstart = packetstart
            refreshtime = refreshtime + 1
    	    if refreshtime >= 30:
                if internet_on():
                    print "STARTING TIME REFRESH"
                    print "----------------------------------"
                    call(["date"])
                    call(["sudo","service","ntp","stop"])
                    call(["sudo","ntpd","-qg"])
                    call(["sudo","service","ntp","start"])
                    call(["date"])
                    print "----------------------------------"
                refreshtime = 0


if __name__ == '__main__':
	main()
