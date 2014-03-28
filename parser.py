#!/usr/bin/env python
"""
	GPS.PY
    v.2

	written by: Manuel Dionne
	credit to: the internet
"""

import sys


"""
function parse packet

returns the time and pos in a GPS packet that looks like this:
START|TIME|POS|END

returns: float time, list position
"""
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
                    if packet[x:len(packet)] == "1|END\n":
                        identifier = 1
                    if packet[x:len(packet)] == "2|END\n":
                        identifier = 2
                finalpos.append(pos[i+1:posend])

        #return the time and list
        return float(time), finalpos, identifier

packet = sys.stdin.read()
time,finalpos,identifier = parse_packet(packet))