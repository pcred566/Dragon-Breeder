import sge
from sge import gfx,dsp
from random import randrange,randint,choice

VERSION = 1.0
FPS=64
greek="αβγδε" # the first 5 letters of the Greek alphabet

def current_fps():
    "Returns rate the game is running at in fps."
    return round(1/(sge.game.regulate_speed(None)/1000),2);

def top_obj(obj,x,y):
    """"Finds the object of type 'obj' that has the largest z-value
        at point (x,y). Returns None if no objects collide at (x,y).
        Follows convention that if 'obj' is None, all object types collide."""
    colliding = sge.collision.rectangle(x,y,1,1,obj)
    if len(colliding) == 0: return None
    
    top = colliding[0]
    for i in range(len(colliding)):
        top = colliding[i] if colliding[i].z > top.z else top
    return top

def resize_sprite(sprite, scale):
    """Resizes the input sprite to 'scale' dimensions; correctly places origin
       and bounding box and places the position at the center of the new sprite.
       If bounding box calculations need to take place, they should happen after
       this function is called (obviously you nitwit)"""

    if scale < 1:
        sprite.scale(scale, scale)
        sprite.resize_canvas(sprite.width*scale,sprite.height*scale)
    else:
        sprite.resize_canvas(sprite.width*scale,sprite.height*scale)
        sprite.scale(scale, scale)
    sprite.bbox_width *= scale; sprite.bbox_height *= scale
    sprite.bbox_width = int(sprite.bbox_width)
    sprite.bbox_height = int(sprite.bbox_height)
    sprite.origin_x = sprite.bbox_width//2
    sprite.origin_y = sprite.bbox_height//2
    sprite.bbox_x = -sprite.origin_x
    sprite.bbox_y = -sprite.origin_y

def recolor(sprite, col1, texsprite, col2, rel):
    """Recolors sprite 1 with col1, texture sprite with col2, then overlays
       resulting texsprite onto resulting sprite. 'rel' is a number that represents
       the location the texture should be drawn relative to sprite when it is overlaid."""
    # overlay main sprite color
    sprite.draw_rectangle(0,0,sprite.width,sprite.height,fill=col1,
                          blend_mode=sge.BLEND_RGBA_MULTIPLY)
    # white temp sprite same size as texture
    temp = gfx.Sprite(width=texsprite.width,height=texsprite.height)
    temp.draw_rectangle(0,0,temp.width,temp.height,fill=gfx.Color('white'))
    
    # Refresh texture sprite to white
    texsprite.draw_rectangle(0,0,temp.width,temp.height,fill=gfx.Color('white'),
                             blend_mode=sge.BLEND_RGB_MAXIMUM)
    # Recolor textured parts of image
    texsprite.draw_rectangle(0,0,temp.width,temp.height,fill=col2,
                             blend_mode=sge.BLEND_RGBA_MULTIPLY)
    # After next line, temp is now a white box with color texture overlaid
    temp.draw_sprite(texsprite,0,0,0)
    
    # Overlay result to current sprite using multiply to get rid of the white
    sprite.draw_sprite(temp,0,rel,rel,
                            blend_mode=sge.BLEND_RGBA_MULTIPLY)

def randcol():
    """Returns a random color with no alpha."""
    col = [randint(0,255) for _ in range(3)]
    return gfx.Color(tuple(col))

def saturated_randcol():
    """Returns a random color that is guaranteed to be fully saturated."""
    # one channel is zero, one is random and one is max
    channels = [0,randint(0,255),255]
    col = [0,0,0]
    
    for i in range(3):
        channel = choice(channels)
        col[i] = channel
        channels.remove(channel)
    
    return gfx.Color(tuple(col))

def pastel_randcol():
    """Returns a random color that is guaranteed to have low saturation
       and medium-to-high brightness."""
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

def desaturated_randcol(saturation,brightness):
    """Returns a random color that is guaranteed to have low-ish saturation.
       Brightness of output is ceiling-ed at 253 to contrast with pure white,
       and floor-ed at 10 to contrast with pure black (outlines of sprites etc.)
       The 'saturation' input controls how desaturated the color should be.
       This value should both be in the range (0,255)."""
    # begin with greyscale
    brightness = 25 if brightness < 25 else brightness
    sat = 255-brightness if saturation > 255-brightness else saturation
    col = [brightness,brightness,brightness]
    for i in range(3):
        col[i] += randint(-sat,sat)
        col[i] += brightness
        col[i] = min(col[i],253)
        col[i] = max(col[i],0)
    
    return gfx.Color(tuple(col))

def calc_bbox(sprite, frame):
    """Returns a 4-tuple containing bounding box x,y,width, and height
       based on the input sprite. Also works with respect to individual
       frames. The implementation is to search a limited number of rows
       and columns to find the smallest area that encloses all of the
       non-alpha pixels in the image. This will occasionally fail as only
       a small number of rows and columns are tested, but it runs in
       constant time so really you should be happy about that. If your sprite
       is very sparse, this will probably end up returning a bbox the size of
       the whole image but then again that isn't really an issue because if
       you want the user to click on tiny particles then just use precise
       collision detection. If it can't find anything it returns the full area."""
    if sprite == None:
        return 0,0,0,0
    
    interval = 5
    
    bbox_x=0
    bbox_width=sprite.width
    bbox_r=bbox_width
    
    bbox_y=0
    bbox_height=sprite.height
    bbox_b=bbox_height

    rowlength = sprite.bbox_width
    collength = sprite.bbox_height
    region = sprite.width//interval
    if region == 0: region = 1
    for i in range(interval):
        
        i = i*region
        for p in range(rowlength//2):
            if p >= rowlength or i >= collength: break
            pixel = sprite.get_pixel(p, i, frame)
            if pixel.alpha != 0:
                if p < bbox_x or bbox_x == 0:
                    bbox_x = p
            pixel = sprite.get_pixel(rowlength-p-1,i,frame)
            if pixel.alpha != 0:
                if rowlength-p-1 > bbox_r or bbox_r == sprite.width:
                    bbox_r = rowlength-p-1

    region = sprite.height//interval
    if region == 0: region = 2
    for i in range(interval):
        
        i *= region
        for p in range(collength//2):
            if p >= collength or i >= rowlength: break
            pixel = sprite.get_pixel(i, p, frame)
            if pixel.alpha != 0:
                if p < bbox_y or bbox_y == 0:
                    bbox_y = p
            pixel = sprite.get_pixel(i,collength-p-1,frame)
            if pixel.alpha != 0:
                if collength-p-1 > bbox_b or bbox_b == sprite.height:
                    bbox_b = collength-p-1

    bbox_width  = bbox_r - bbox_x
    bbox_height = bbox_b - bbox_y
    bbox_x -= sprite.origin_x
    bbox_y -= sprite.origin_y
   
    return bbox_x, bbox_y, bbox_width, bbox_height

