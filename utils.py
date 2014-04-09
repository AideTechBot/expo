# pyglet.utils.py
# www.akeric.com - 2011-03-17
# utils to make pyglet easier to work with, help my learning of it.
import math
import pyglet
from pyglet.gl import *

def screenshot(name='screenshot'):
    """
    Take a screenshot

    Parameters:
    name : string : Default 'screenshot'.  Name of the saved image.  Will
        always save as .png
    """
    # Get the 'the back-left color buffer'
    pyglet.image.get_buffer_manager().get_color_buffer().save('%s.png'%name)

def getPixelValue(x, y):
    """
    Return the RGBA 0-255 color value of the pixel at the x,y position.
    """
    # BufferManager, ColorBufferImage
    color_buffer = pyglet.image.get_buffer_manager().get_color_buffer()
    # AbstractImage, ImageData, sequece of bytes
    pix = color_buffer.get_region(x,y,1,1).get_image_data().get_data("RGBA", 4)
    return pix[0], pix[1], pix[2], pix[3]

def drawPoint(x, y, color):
    """
    Based on the (r,g,b) color passed in, draw a point at the given x,y coord.
    """
    pyglet.graphics.draw(1, GL_POINTS,
                         ('v2i', (x, y)),
                         ('c3B', (color[0], color[1], color[2]) ) )

def getSmoothConfig():
    """
    Sets up a configuration that allows of smoothing\antialiasing.
    The return of this is passed to the config parameter of the created window.
    """
    try:
        # Try and create a window config with multisampling (antialiasing)
        config = Config(sample_buffers=1, samples=4,
                        depth_size=16, double_buffer=True)
    except pyglet.window.NoSuchConfigException:
        print "Smooth contex could not be aquiried."
        config = None
    return config

def printEvents(window):
    """
    Debug tool that will print the events to the console.

    window is an instance of a Window object receiving the events.
    """
    window.push_handlers(pyglet.window.event.WindowEventLogger())

def playMusic(music):
    """
    Simple wrapper to play a music (mp3) file.

    music : music file relative to application.
    """
    music = pyglet.resource.media(music)
    music.play()

def setBackgroundColor(r,g,b):
    """
    Color is a list of four values, [r,g,b,a], each from 0 -> 1
    """
    pyglet.gl.glClearColor(r,g,b,1)

def makepositive(int):
    if(int < 0):
        return int * -1
    else:
        return int

def getdistance(x,y,xa,ya):
    a = xa - x
    b = ya - y
    xs = math.pow(a,2)
    ys = math.pow(b,2)
    c = xs + ys
    dist = math.sqrt(c)

    return round(dist,1)

"""
LINK FOR CIRCLE CIRCLE INTERSECTION:
http://paulbourke.net/geometry/circlesphere/
"""
def findintersect(circle1,circle2):
    coords = ["",0,0,0,0]
    if(round(circle1[2],0) == 0.0 or round(circle2[2],0) == 0.0):
        coords[0] = "UTILS: one circle or both have a null radius"
        return coords
    if(getdistance(circle1[0],circle1[1],circle2[0],circle2[1]) > circle1[2] + circle2[2]):
        coords[0] = "UTILS: seperate circles"
        return coords
    if(getdistance(circle1[0],circle1[1],circle2[0],circle2[1]) < makepositive(circle1[2] - circle2[2])):
        coords[0] = "UTILS: circles are inside eachother"
        return coords
    if(getdistance(circle1[0],circle1[1],circle2[0],circle2[1]) == 0 and circle1[2] == circle2[2]):
        coords[0] = "UTILS: infinite intersections found"
        return coords
    if(getdistance(circle1[0],circle1[1],circle2[0],circle2[1]) == circle1[2] + circle2[2]):
        points = 1

    #Distances
    d = getdistance(circle1[0],circle1[1],circle2[0],circle2[1])
    dx = circle2[0] - circle1[0]
    dy = circle2[1] - circle1[1]
    #a and h
    a = (circle1[2]**2 - circle2[2]**2 + d**2) / (2 * d)
    h = math.sqrt(makepositive(circle1[2]**2 - a**2))

    #Point 2
    x2 = circle1[0] + (dx * a/d)
    y2 = circle1[1] + (dy * a/d)

    #If theres only one intersection: return here
    if(d == circle1[2] + circle1[2]):
        coords[0] = "UTILS: one intersection found"
        coords[1] = x2
        coords[2] = y2
        return coords

    #Determine the offset from point 2
    rx = -dy * (h/d)
    ry = dx * (h/d)

    #Determine the absolute intersection points OH BOY 
    coords[1] = round(x2 + rx,0)
    coords[3] = round(x2 - rx,0)
    coords[2] = round(y2 + ry,0)
    coords[4] = round(y2 - ry,0)

    #Return the final coordinates array which should look like [ "status str", x, y, x_prime, y_prime ]
    coords[0] = "UTILS: two intersections found"
    return coords


"""
function parse packet

returns the time and pos in a GPS packet that looks like this:
START|TIME|POS|IDENTIFIER|END

returns: float time, list position, int identifier
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

def internet_on():
    try:
        response=urllib2.urlopen('http://74.125.228.100',timeout=1)
        return True
    except urllib2.URLError as err: pass
    return False
