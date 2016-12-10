import sge
from sge import gfx,dsp,collision
from random import randrange,randint,choice
 
hash_table = [168, 175, 53, 13, 167, 180, 50, 255, 102, 62,
              57, 174, 91, 55, 244, 97, 241, 14, 34, 178,
              161, 251, 104, 206, 31, 60, 198, 15, 235, 144,
              38, 64, 187, 106, 72, 149, 214, 110, 186, 131,
              5, 92, 132, 74, 107, 129, 184, 10, 138, 155, 243,
              137, 176, 121, 79, 225, 84, 22, 185, 18, 71, 147,
              221, 211, 7, 49, 233, 78, 220, 154, 96, 11, 37, 253,
              196, 101, 236, 248, 205, 237, 67, 204, 226, 75, 36,
              140, 239, 20, 133, 190, 95, 194, 87, 98, 188, 42, 130,
              35, 209, 99, 108, 3, 46, 245, 224, 210, 145, 200, 246,
              83, 25, 117, 30, 43, 105, 254, 82, 85, 94, 218, 123,
              164, 177, 48, 247, 146, 215, 189, 231, 51, 150, 136,
              23, 66, 8, 229, 0, 61, 179, 86, 77, 223, 76, 41, 126,
              202, 157, 59, 227, 47, 191, 169, 208, 139, 230, 73, 240,
              100, 232, 207, 182, 40, 39, 122, 170, 143, 172, 192, 119,
              148, 17, 249, 213, 93, 124, 219, 242, 63, 112, 159, 103,
              156, 33, 238, 12, 135, 153, 173, 4, 181, 151, 2, 216, 80,
              152, 109, 56, 197, 27, 165, 250, 1, 217, 116, 6, 16, 113,
              65, 142, 118, 128, 134, 160, 115, 125, 228, 203, 28, 58,
              120, 222, 183, 26, 19, 68, 201, 29, 88, 252, 199, 212, 127,
              90, 163, 234, 32, 24, 114, 45, 54, 111, 195, 162, 21, 44, 158,
              141, 89, 69, 193, 81, 166, 52, 171, 9, 70]

VERSION = 1.0
FPS=64
greek="αβγδε" # the first 5 letters of the Greek alphabet

def current_fps():
    "Returns rate the game is running at in fps."
    return round(1/(sge.game.regulate_speed(None)/1000),2);

def clamp(num,start,end):
    """Returns 'num' if num >= start and num <= end, else forces into range."""
    if num >= start and num <= end: return num
    elif num < start: return start
    elif num > end: return end

def top_obj(obj,x,y):
    """"Finds the object of type 'obj' that has the largest z-value
        at point (x,y). Returns None if no objects collide at (x,y).
        Follows convention that if 'obj' is None, all object types collide."""
    colliding = collision.rectangle(x,y,1,1,obj)
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
    """Recolors sprite 1 with col1, texsprite with col2, then overlays resulting
       texsprite onto resulting sprite. 'rel' is a number that represents the
       location the texture should be drawn relative to sprite when it is overlaid."""
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

def desaturated_randcol(saturation,brightness=100):
    """Returns a random color that is guaranteed to have low-ish saturation.
       Brightness of output is ceiling-ed at 253 to contrast with pure white,
       and floor-ed at 10 to contrast with pure black (outlines of sprites etc.)
       The 'saturation' input controls how desaturated the color should be.
       This value should both be in the range (0,255)."""
    # begin with greyscale
    brightness = clamp(brightness,25,255)
    sat = clamp(saturation,0,255-brightness)
    col = [brightness,brightness,brightness]
    for i in range(3):
        col[i] += randint(-sat,sat)
        col[i] += brightness
        col[i] = min(col[i],253)
        col[i] = max(col[i],0)
    
    return gfx.Color(tuple(col))

def gen_secondary_col(primary):
    """Uses a color hash to generate a secondary color given the primary.
       Always produces the same output on a given input, but comparatively
       the output color can appear to be totally random."""
    r,g,b = primary.red,primary.green,primary.blue
    return primary

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

