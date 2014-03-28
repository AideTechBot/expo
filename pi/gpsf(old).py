#!/usr/bin/python
"""
     GPS.PY

     written by: Manuel Dionne
     credit to: the internet
"""
import wave
import PiFm
import time
import os
from subprocess import call


def send_data( filename, freq ):
   call(["./pifm", filename, freq])
   return

freq = 500.0
data_size = 0
frate = 11025.0  # framerate as a float
amp = 64000.     # multiplier for amplitude
pos = "400 600"
fname = "packet.wav"
data_list_x = []

def cleardata():
     if os.path.exists(fname):
          os.remove(fname)
     else:
          print "No file to delete: " + fname

def writedata():
     global data_list_x
     wav = wave.open(fname,'w')

     #padding 
     padding = ""
     i = 0
     for i in range(0,1024):
          i = i + 1
          padding = padding + "A"
     print padding

     #making the data
     data = padding + "START" + "|" + str(time.time()) + "|" + pos + "|" + "END" + padding + "\n"
     data_size = len(data)
     print  str(data) + str(data_size)

     #put all the data in a list
     for x in range(data_size):
        data_list_x.append(data[x])

     #declaring some vars
     nchannels = 1
     sampwidth = 2
     framerate = int(frate)
     nframes = data_size
     comptype = "NONE"
     compname = "not compressed"

     #setting the params
     wav.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))
    
     #writing frames
     for s in data_list_x:
     	wav.writeframes(s)
     wav.close()

     #recycle vars
     data_list_x = []

while(True):
     cleardata()
     writedata()
     print "ok"
     send_data(fname,"103.3")
     time.sleep(1)