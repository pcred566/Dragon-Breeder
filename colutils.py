from sge import gfx
from sge.gfx import Sprite,Color
from random import randint,choice

FPS = 64
PAUSE = False
w = 360 # convenience, width of window
h = 240 # convenience, height of window

def clamp(num,start,end):
    """Returns 'num' if num >= start and num <= end, else forces into range."""
    if num >= start and num <= end: return num
    elif num < start: return start
    elif num > end: return end

def randcol():
    """Returns a random color with full alpha."""
    col = [randint(0,255) for _ in range(3)]
    return gfx.Color(tuple(col))

def saturated_randcol(value=255):
    """Returns a random color that is guaranteed to be fully saturated.
       Min brightness clamped to 40."""
    # one channel is zero, one is random and one is max
    channels = [0,randint(0,255),255]
    col = [0,0,0]
    value = clamp(value,40,255)
    
    for i in range(3):
        channel = choice(channels)
        col[i] = channel*value//255
        channels.remove(channel)
    
    return gfx.Color(tuple(col))

def pastel_randcol():
    """Returns a random color that is guaranteed to have low saturation
       and high brightness like a pastel color."""
    # begin with saturated then desaturate
    col = saturated_randcol()
    offset = 175
    
    for i in range(3):
        if col[i] == 255:
            continue
        elif col[i] != 0:
            col[i] = min(col[i]+offset,255)
        else:
            col[i] += offset
    
    return gfx.Color(tuple(col))

def desaturated_randcol(saturation,brightness=100):
    """Returns a random color that is guaranteed to have low-ish saturation.
       Brightness of output is ceiling-ed at 253 to contrast with pure white,
       and floor-ed at 40 to contrast with pure black (outlines of sprites etc.)
       The 'saturation' input controls how desaturated the color should be.
       This value should both be in the range (0,255)."""
    # begin with greyscale
    brightness = clamp(brightness,40,255)
    sat = clamp(saturation,0,255-brightness)
    col = [brightness,brightness,brightness]
    
    for i in range(3):
        r = randint(-sat,sat)
        if abs(r-brightness) < sat//2: # minimum saturation = sat / 2
            if r < 0:
                r = randint(-sat,-sat//2)
            else:
                r = randint(sat//2,sat)
        col[i] += r
        col[i] = clamp(col[i],50,253)

    return gfx.Color(col)
