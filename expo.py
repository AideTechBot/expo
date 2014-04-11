"""
    GPS DEMONSTRATION
    v.1

    written by: Manuel Dionne
    credit to: the internet
"""
import pyglet
from pyglet.gl import *
from pyglet.window import key
from pyglet.window import mouse
import primitives
import sys
import threading
import socket
from decimal import *
from threading import Thread
from utils import *

data = []
FPS = 60
address = ("", 9090)
config = pyglet.gl.Config(sample_buffers=1, samples=4)
baud = '60'
mark_freq = '20300'
space_freq = '20250'
confidence = '0.4'
calc_factor = Decimal(0.250)
getcontext().prec = 6


class PrimWin(pyglet.window.Window):

    def __init__(self):
        super(PrimWin, self).__init__(fullscreen=True,config=config, caption='GPS')
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        #initializing some variables for certain handlers
        self.linesvisible = False
        self.circlesvisible = False
        self.fpsvisible = False
        self.mousedown = False
        self.dragable = False
        self.coordlabelvisible = False
        #debug off
        self.debug = False

        #primitives initializing
        self.cone = primitives.Circle(425,625,width=100,color=(1,0,0,0.5))
        self.ctwo = primitives.Circle(925,725,width=100,color=(0,1,0,0.5))
        self.cthree = primitives.Circle(825,225,width=100,color=(0,0,1,0.5))

        self.lone = primitives.Line((0,0),(100,100),stroke=2,color=(0,0,0,1))
        self.ltwo = primitives.Line((0,0),(100,100),stroke=2,color=(0,0,0,1))
        self.lthree = primitives.Line((0,0),(100,100),stroke=2,color=(0,0,0,1))
        self.ldebug = primitives.Line((0,1065),(1920,1065),stroke=30,color=(0,0,0,0.5))
        #self.p = primitives.Pixel(10,10)
        #self.a = primitives.Arc(150,150,radius=100,color=(1.,0.,0.,1.),sweep=90,style=GLU_FILL)
        #self.P = primitives.Polygon([(0, 0), (50, 200), (80, 200),(60,100),(100,5)],color=(.3,0.2,0.5,.7))
        
        #Labels
        self.distlabelone = pyglet.text.Label('distance',font_name='Arial',font_size=20, x=0, y=10, color=(0,0,0,255))
        self.distlabeltwo = pyglet.text.Label('distance',font_name='Arial',font_size=20, x=0, y=10, color=(0,0,0,255))
        self.distlabelthree = pyglet.text.Label('distance',font_name='Arial',font_size=20, x=0, y=10, color=(0,0,0,255))
        self.coordlabel = pyglet.text.Label('coord',font_name='Arial',font_size=20, x=700, y=50, color=(0,0,0,255))
        self.debuglabel = pyglet.text.Label('debug',font_name='Lucida Console',font_size=20, x=10, y=1056, color=(255,255,255,255))

        #Images
        self.satimage = pyglet.resource.image('sat.png')
        self.gpsimage = pyglet.resource.image('gps.png')
        self.cursorimage = pyglet.resource.image('blank.png')
        self.grid = pyglet.resource.image('grid.png')

        #cursor
        #self.cursor = pyglet.window.ImageMouseCursor(self.cursorimage, 5, 5)
        #self.set_mouse_cursor(self.cursor)

        #batch and sprites
        self.batch = pyglet.graphics.Batch()

        self.sprites = [pyglet.sprite.Sprite(self.gpsimage, batch=self.batch),
                        pyglet.sprite.Sprite(self.satimage, batch=self.batch),
                        pyglet.sprite.Sprite(self.satimage, batch=self.batch),
                        pyglet.sprite.Sprite(self.satimage, batch=self.batch)
                       ]
        self.gridsprite = pyglet.sprite.Sprite(self.grid)

        # Setup debug framerate display:
        self.fps_display = pyglet.clock.ClockDisplay()
       
        # Schedule the update of this window, so it will advance in time at the
        # defined framerate.  If we don't, the window will only update on events
        # like mouse motion.
        pyglet.clock.schedule_interval(self.update, 1.0/FPS)

    def on_draw(self):
        # Window event
        setBackgroundColor(1,1,1)
        self.clear()

        #Make the background a grid
        self.gridsprite.draw()

        #render the circles if it's turned on
        if self.circlesvisible:
            self.cone.render()
            self.ctwo.render()
            self.cthree.render()

        #render lines if it's turned on
        if self.linesvisible:
            self.lone.render()
            self.ltwo.render()
            self.lthree.render()
            self.distlabelone.draw()
            self.distlabeltwo.draw()
            self.distlabelthree.draw()

        #render the coords
        if self.coordlabelvisible:
            self.coordlabel.draw()


        #debug box    
        if self.debug:
            self.ldebug.render()
            self.debuglabel.draw()

        #self.p.render()
        #self.a.render()
        #self.P.render()
        #self.l.render()
        self.batch.draw()
        #set the default position of the satallites(we will change this later to be dynamic and maybe update their position) <-- made it dynamic :D
        if not self.dragable:
            if data:
                if data[3] == 1:
                    self.sprites[1].x = int(data[2][0]) - 25
                    self.sprites[1].y = int(data[2][1]) - 25
                    self.cone.x = int(data[2][0])
                    self.cone.y = int(data[2][1])
                if data[3] == 2:
                    self.sprites[2].x = int(data[2][0]) - 25
                    self.sprites[2].y = int(data[2][1]) - 25
                    self.ctwo.x = int(data[2][0])
                    self.ctwo.y = int(data[2][1])
        else:
            self.sprites[1].x = 400
            self.sprites[1].y = 600
            self.sprites[2].x = 900
            self.sprites[2].y = 700
            self.cone.x = 425
            self.cone.y = 625
            self.ctwo.x = 925
            self.ctwo.y = 725
        self.sprites[3].x = 800
        self.sprites[3].y = 200

        if self.fpsvisible:
            self.fps_display.draw()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.dragable:
            if buttons & mouse.LEFT:
                if x > self.sprites[0].x and x < (self.sprites[0].x + 1000):
                    if y > self.sprites[0].y and y < (self.sprites[0].y + 1000):
                        self.debuglabel.text = "Mouse drag"
                        self.sprites[0].x = x - 25
                        self.sprites[0].y = y - 25

    def update(self, dt):
        # Scheduled event

        #set the labels position
        self.distlabelone.x = 100
        self.distlabeltwo.x = 100
        self.distlabelthree.x = 100
        self.distlabelone.y = 100
        self.distlabeltwo.y = 75
        self.distlabelthree.y = 50

        #sat 3 is hardcoded
        self.distlabelthree.text = "Dist. a SAT3: %s"% str(getdistance(self.sprites[0].x,self.sprites[0].y,self.sprites[3].x,self.sprites[3].y))
        self.cthree.radius = getdistance(self.sprites[0].x,self.sprites[0].y,self.sprites[3].x,self.sprites[3].y)

        #packet handling
        print "----", self.dragable, data
        if not self.dragable:
            if data:
                print "yes"
                if data[3] == 1:
                    self.cone.radius = int(data[1])
                    self.distlabelone.text = "Dist. a SAT1: %s"% str(data[1])
                if data[3] == 2:
                    self.ctwo.radius = int(data[1])
                    self.distlabeltwo.text = "Dist. a SAT2: %s"% str(data[1])
        else:
            self.distlabelone.text = "Dist. a SAT1: %s"% str(getdistance(self.sprites[0].x,self.sprites[0].y,self.sprites[1].x,self.sprites[1].y))
            self.distlabeltwo.text = "Dist. a SAT2: %s"% str(getdistance(self.sprites[0].x,self.sprites[0].y,self.sprites[2].x,self.sprites[2].y))

            #set the size of the circles depending on were the gps is
            self.cone.radius = getdistance(self.sprites[0].x,self.sprites[0].y,self.sprites[1].x,self.sprites[1].y)
            self.ctwo.radius = getdistance(self.sprites[0].x,self.sprites[0].y,self.sprites[2].x,self.sprites[2].y)

        #set the coords
        if not self.dragable:
                SAT1circle = [self.sprites[1].x,self.sprites[1].y,self.cone.radius]
                SAT2circle = [self.sprites[2].x,self.sprites[2].y,self.ctwo.radius]
        else:
            SAT1circle = [self.sprites[1].x,self.sprites[1].y,getdistance(self.sprites[0].x,self.sprites[0].y,self.sprites[1].x,self.sprites[1].y)]
            SAT2circle = [self.sprites[2].x,self.sprites[2].y,getdistance(self.sprites[0].x,self.sprites[0].y,self.sprites[2].x,self.sprites[2].y)]

        #alone once again :(
        SAT3circle = [self.sprites[3].x,self.sprites[3].y,getdistance(self.sprites[0].x,self.sprites[0].y,self.sprites[3].x,self.sprites[3].y)]

        #set the a and b points for the lines
        self.lone.a2 = (self.sprites[0].x - 25, self.sprites[0].y - 25)
        self.ltwo.a2 = (self.sprites[0].x - 25, self.sprites[0].y -25)
        self.lthree.a2 = (self.sprites[0].x - 25, self.sprites[0].y - 25)
        self.lone.b2 = (self.sprites[1].x - 25, self.sprites[1].y - 25)
        self.ltwo.b2 = (self.sprites[2].x - 25, self.sprites[2].y - 25)
        self.lthree.b2 = (self.sprites[3].x - 25, self.sprites[3].y - 25)
        
        SAT1_SAT2 = findintersect(SAT1circle,SAT2circle)
        #print "sat1 to sat2", SAT1_SAT2
        SAT2_SAT3 = findintersect(SAT2circle,SAT3circle)
        #print "sat2 to sat3", SAT2_SAT3

        #set the coord str to whatever
        coords = "N/A"
        if(SAT1_SAT2[1] == SAT2_SAT3[1] and SAT1_SAT2[2] == SAT2_SAT3[2]):
            coords = "'{0}', '{1}'".format(int(SAT1_SAT2[1]), int(SAT1_SAT2[2]))

        if(SAT1_SAT2[3] == SAT2_SAT3[3] and SAT1_SAT2[4] == SAT2_SAT3[4]):
            coords = "'{0}', '{1}'".format(int(SAT1_SAT2[3]), int(SAT1_SAT2[4]))

        if(SAT1_SAT2[1] == SAT2_SAT3[3] and SAT1_SAT2[2] == SAT2_SAT3[4]):
            coords = "'{0}', '{1}'".format(int(SAT1_SAT2[1]), int(SAT1_SAT2[2]))

        if(SAT1_SAT2[3] == SAT2_SAT3[1] and SAT1_SAT2[4] == SAT2_SAT3[2]):
            coords = "'{0}', '{1}'".format(int(SAT1_SAT2[3]), int(SAT1_SAT2[4]))
        #and finally updating the label and setting the gps pos
        self.coordlabel.text = "Coord. du GPS: %s" % coords
        if not coords == "N/A":
            #yeah yeah, I know, code execution vunerability, whatever
            exec("coords = [" + coords + "]")
            self.sprites[0].x = int(coords[0])
            self.sprites[0].y = int(coords[1])

            
    def on_key_press(self, symbol, modifiers):
        #keypress event
        if symbol == key.P:
            self.debuglabel.text = "Screenshot!"
            screenshot()
        if symbol == key.F3:
            if self.debug:
                self.debug = False
                self.fpsvisible = False
            else:
                self.debug = True
                self.fpsvisible = True              
        if symbol == key.L:
            if self.linesvisible:
                self.debuglabel.text = "Hiding lines"
                self.linesvisible = False
            else:
                self.debuglabel.text = "Showing lines"
                self.linesvisible = True
        if symbol == key.C:
            if self.circlesvisible:
                self.debuglabel.text = "Hiding circles"
                self.circlesvisible = False
            else:
                self.debuglabel.text = "Showing circles"
                self.circlesvisible = True
        if symbol == key.D:
            if self.dragable:
                self.debuglabel.text = "Objects are no longer dragable"
                self.dragable = False
            else:
                self.debuglabel.text = "Objects are now dragable"
                self.dragable = True
        if symbol == key.EQUAL:
            if self.coordlabelvisible:
                self.debuglabel.text = "Showing coords"
                self.coordlabelvisible = False
            else:
                self.debuglabel.text = "Hiding coords"
                self.coordlabelvisible = True
        if symbol == key.ESCAPE:
            self.on_close()

#packet handling
def packethandler():
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(address)
        message, addr = sock.recvfrom(2048)
        sock.close()
        print message
        try:
            #even better!  a REMOTE code execution vunerability!
            exec(message)
        except Exception, e:
            print "GOT AN ERROR: ", e
        print packet
        global data
        data = packet


if __name__ == '__main__':
    PrimWin()
    packetreception = Thread(target = packethandler).start()
    window = Thread(target = sys.exit, args = (pyglet.app.run())).start()