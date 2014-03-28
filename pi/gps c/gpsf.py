#!/usr/bin/env python
"""
     GPS.PY

     written by: Manuel Dionne
     credit to: the internet
"""
import time
import os
import urllib2
from subprocess import *

fname = "send.wav"
baud = "60"
mark_freq = "20300"
space_freq = "20250"
#set sr to 18000 for working radio tranmission
sample_rate = "48000"
pos = "300_600"
identifier = 1

def internet_on():
    try:
        response=urllib2.urlopen('http://74.125.228.100',timeout=1)
        return True
    except urllib2.URLError as err: pass
    return False

def send_data( filename, freq ):
   call(["sudo","aplay", filename,"-f","S16_LE"])
   return

def createdata():

     #making the data
     data = "|START" + "|" + str("%.6f" % time.time()) + "|" + pos + "|" + str(identifier) + "|" + "END"
     data_size = "\n" + str(len(data))
     print  str(data) + str(data_size)

     return str(data)

def encodedata(data):
     start = float(str("%.20f" % time.time()))
     p1 = Popen(["echo", "-e","\"" + data + "\""], stdout=PIPE)
     p2 = Popen(["sudo", "./minimodem", "--tx", "-8", "-f", fname, baud, "--space", space_freq, "--mark", mark_freq], stdin=p1.stdout, stdout=PIPE)
     stop = float(str("%.20f" % time.time()))
     print "[GPS] Encode time: ", stop - start
     output = p2.communicate()[0]
     print output

refreshtime = 29
while(True):
     data = createdata()
     print "[GPS] packet created: " + data
     encodedata(data)
     print "[GPS] data encoded"
     print "[GPS] sending out packet"
     send_data(fname,"105.0")
     print "[GPS] sleeping..."
     time.sleep(2)
     refreshtime = refreshtime + 1
     if refreshtime >= 30:
          if internet_on():
               print "[GPS] STARTING TIME REFRESH"
               print "----------------------------------"
               call(["date"])
               call(["sudo","service","ntp","stop"])
               call(["sudo","ntpd","-qg"])
               call(["sudo","service","ntp","start"])
               call(["date"])
               print "----------------------------------"
          refreshtime = 0
