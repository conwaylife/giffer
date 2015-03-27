# Runs the current selection for a given number of steps and
# creates a black and white animated GIF file.
# Based on giffer.pl, which is based on code by Tony Smith.

import golly as g
import os
import struct

rect=g.getselrect()
if len(rect)==0:
    g.exit("Nothing in selection.")
[x,y,width,height]=rect
if(width>=65536 or height>=65536):
    g.exit("The width or height of the GIF file must be less than 65536 pixels.")

frames = pause = cellsize = gridwidth = vx = vy = filename = "?"
gridwidth = "2"
def getparam(msg):
    info = "Current parameters:\n"\
        +"The number of frames: "+frames+"\n"\
        +"The pause time of each frame: "+pause+"centisecs\n"\
        +"The size of each cell: "+cellsize+"px\n"\
        +"(The width of gridlines: "+gridwidth+"px -- fixed)\n"\
        +"The speed of the pattern: "+"("+vx+","+vy+")px/frame\n"\
        +"The file name: "+filename+"\n\n"
    return g.getstring(info+msg, "", "Create animated GIF")
frames = getparam("Enter the number of frames.")          
pause = getparam("Enter the pause time of each frame (in centisecs.)")
cellsize = getparam("Enter the size of each cell (in pixels.)")
# GridLines are 2 pixels in LifeWiki gif format.
# gridwidth = getparam("Enter the width of gridlines (in pixels, 0 to disable.)")
vx, vy = getparam("Enter the speed of the pattern (in pixels per frame.)\n ex)(-3,5)px/frame -> -3 5").split()
filename = getparam("Enter the file name. ex)out.gif")
    
def tryint(var, name):
    try:
        return int(var)
    except:
        g.exit(name + " is not an integer: " + var)
frames = tryint(frames, "Number of frames")
pause = tryint(pause, "Pause time")
cellsize = tryint(cellsize, "Cell Size")
gridwidth = tryint(gridwidth, "Grid Width")
vx = tryint(vx, "X velocity")
vy = tryint(vy, "Y velocity")
canvasheight = (cellsize+gridwidth)*height+gridwidth
canvaswidth = (cellsize+gridwidth)*width+gridwidth
if(canvaswidth>=65536 or canvasheight>=65536):
    g.exit("The width or height of the GIF file must be less than 65536 pixels."
            + "Width: " + canvaswidth + "Height: " + canvasheight)
# ------------------------------------------------------------------------------
def getpx(xrel, yrel, frameidx):
    xabs = xrel + vx * frameidx
    yabs = yrel + vy * frameidx
    if(xabs%(cellsize+gridwidth)<gridwidth or yabs%(cellsize+gridwidth)<gridwidth):
        return "2"
    else: return str(g.getcell(x+xabs/(cellsize+gridwidth), y+yabs/(cellsize+gridwidth)))

def getdata(frameidx):
    lines = []
    # Each array element is a line of 0 and 1 characters
    for ypx in xrange(canvasheight):
        line = ""
        for xpx in xrange(canvaswidth):
            line += getpx(xpx, ypx, frameidx)
        lines += line
    return lines
# ------------------------------------------------------------------------------
def compress(lines):
    table = {'0': 0, '1': 1, '2': 2, '3': 3}
    curr = cc = 4
    used = eoi = 5
    bits = size = 3
    mask = 7
    output = code = ""
    for line in lines:
        for i in xrange(len(line)):
            next = line[i]
            if (code + next) in table:
                code += next
            else:
                used += 1
                table[(code + next)] = used
                curr += table[code] << bits
                bits += size
                while(bits >= 8):
                    output += chr(curr & 255)
                    curr >>= 8
                    bits -= 8
                if(used > mask):
                    if(size < 12):
                        size += 1
                        mask = mask*2 + 1
                    else:
                        curr += cc << bits # output cc in current width
                        bits += size
                        while(bits >= 8):
                            output += chr(curr & 255)
                            curr >>= 8
                            bits -= 8
                        table = {'0': 0, '1': 1} #reset table
                        used = 5
                        bits = 3
                        mask = 7
                code = next
    curr += table[code] << bits
    bits += size
    while(bits >= 8):
        output += chr(curr & 255)
        curr >>= 8
        bits -= 8
    output += chr(curr)
    subbed = ""
    while(len(output) > 255):
        subbed += chr(255) + output[:255]
        output = output[255:]
    return subbed + chr(len(output)) + output + chr(0)
# ----------------------------------------------------------------------
# GIF formatting
# Useful information of GIF formats in:
# http://www.matthewflickinger.com/lab/whatsinagif/bits_and_bytes.asp
# ----------------------------------------------------------------------
header = "GIF89a"
screendesc = struct.pack("<2HB2b", canvaswidth, canvasheight, 0x91, 0, 0)
# Colors in colortable: White, Black, LifeWiki Gray, and Black(Unused) (3 bytes each)
colortable = "\xFF\xFF\xFF\x00\x00\x00\xC6\xC6\xC6\x00\x00\x00"
applic = "\x21\xFF\x0B" + "NETSCAPE2.0" + struct.pack("<2bHb", 3, 1, 0, 0)
imagedesc = struct.pack("<4HB", 0, 0, canvaswidth, canvasheight, 0x00)

try:
    gif = open(os.path.join(os.getcwd(), filename),"wb")
except:
    g.exit("Unable to open file.")

gif.write(header + screendesc + colortable + applic)
for f in xrange(frames):
    # Graphics control extension
    gif.write("\x21\xF9" + struct.pack("<bBH2b", 4, 0x00, pause, 0, 0))
    # Get data for this frame
    gif.write("," + imagedesc + chr(2) + compress(getdata(f)))
    g.show(str(f+1)+"/"+str(frames))
    if(f+1 < frames):
        g.run(1)
        g.update()
gif.close()
g.show("GIF animation saved in " + filename)
