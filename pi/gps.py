#!/usr/bin/env python
"""
     GPS.PY
     v.2

     written by: Manuel Dionne
     credit to: the internet
"""
import time
import os
import urllib2
from subprocess import *

fname = "send.wav"
baud = "1000"
pos = "300_600"
identifier = 1

def internet_on():
    try:
        response=urllib2.urlopen('http://74.125.228.100',timeout=1)
        return True
    except urllib2.URLError as err: pass
    return False

def send_data( filename, freq ):
   call(["./PiFmDma", filename, freq])
   return

def createdata():
     #making the data
     data = "START" + "|" + str("%.20f" % time.time()) + "|" + pos + "|" + str(identifier) + "|" + "END" +"\n"
     data_size = len(data)

def encodedata(data):
     p1 = Popen(["echo", "-e","\"" + data + "\""], stdout=PIPE)
     p2 = Popen(["minimodem", "--tx", "-f", fname, "-8", baud], stdin=p1.stdout, stdout=PIPE)
     output = p2.communicate()[0]
     print output

refreshtime = 0
while(True):
     data = createdata()
     print "[GPS] packet created: " + data
     encodedata(data)
     print "[GPS] data encoded"
     print "[GPS] sending out packet"
     send_data(fname,"103.3")
     print "[GPS] sleeping..."
     time.sleep(2)
     refreshtime = refreshtime + 1
     if refreshtime >= 400:
          if internet_on():
               print "[GPS] internet connection found"
               print "[GPS] syncing time..."
               call(["date"])
               call(["sudo","service","ntpd","stop"])
               call(["sudo","ntpd","-qg"])
               call(["sudo","service","ntpd","start"])
               call(["date"])
               print "[GPS] Time synced"
          else:
               print "[GPS] no internet connection: time sync failed"
          refreshtime = 0