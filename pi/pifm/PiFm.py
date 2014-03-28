#!/usr/bin/python

from subprocess import call


def play_sound( filename ):
   call(["sudo", "./pifm", filename])
   return