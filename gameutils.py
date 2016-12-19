import os
import sge
import gzip
import pickle

from dragon import *
from colutils import *
from PIL import Image
from sge import gfx,dsp,collision
from random import randrange,randint,choice
from pygame.image import tostring, frombuffer
from appdirs import user_data_dir,user_cache_dir

VERSION = "1.0"
FPS = 64
appname = "Dragon Breeder v"+VERSION
author = '566 Games'
SAVEDIR = user_data_dir(appname,author)

dragons = []
rooms = []
inventory = {}
money = [0] # god damn python integer immutability
settings = {}

w = 320 # convenience, width of window
h = 240 # convenience, height of window

############### CLASS DEFINITIONS ###############
class Game(dsp.Game):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        global w,h
        w = sge.game.width
        h = sge.game.height
    
    def event_step(self,rt,dt):
        # following line draws region main gameplay occurs in
        # self.project_rectangle(4,4,256,192,fill=gfx.Color('black'))
        bglayers[0].x += 1
        bglayers[0].y += 1

    def event_key_press(self, key, char):

        if key == 'f11':
            scale = self.scale
            if scale == 2: # CYCLE BEGIN HERE
                self.scale = 3
            if scale == 3: # OOH AAH
                self.scale = 4
            if scale == 4: # CYCLE END HERE
                self.scale = 2
        elif key == 'escape':
            self.event_close()
        elif key in ('p', 'enter'):
            self.pause()
            

    def event_close(self):
        self.end()

    def event_paused_key_press(self, key, char):
        if key == 'escape':
            self.event_close()
        else:
            self.unpause()

    def event_paused_close(self):
        self.event_close()

class MenuRoom(dsp.Room):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for obj in self.objects[:]:
            self.remove(obj)
        self.logo = gfx.Sprite('logo','sprites')
        resize_sprite(self.logo,1)
        self.screen = 'MAIN'
        self.buttons = ['START GAME','OPTIONS','HOW TO PLAY','SAVE & QUIT']
        sprites = [gfx.Sprite('button_rectangle','sprites',width=90,height=font.get_height('ASDF')+5)
                   for _ in self.buttons]
        for i in range(len(sprites)):
            sprites[i].draw_text(font,text=self.buttons[i],x=sprites[i].width//2,y=4,halign='center',
                                 color=gfx.Color('white'),anti_alias=False)
            resize_sprite(sprites[i],1)
        
        objs = [dsp.Object(w//2,125+i*20,sprite=sprites[i]) for i in range(len(sprites))]
        for obj in objs:
            self.add(obj)

    def event_mouse_button_press(self,button):
        if  button == 'left' and self.screen == 'MAIN':
            colliding = collision.rectangle(sge.game.mouse.x,sge.game.mouse.y,1,1)
            if not colliding: return
            if colliding[0] == self.objects[0]: # Start game
                MainRoom(background=gfx.Background(
                    [],color=gfx.Color('white'))).start(transition='wipe_left',transition_time=300)
            elif colliding[0] == self.objects[1]: # Options
                self.screen = 'OPTIONS'
            elif colliding[0] == self.objects[2]: # Tutorial
                pass
            elif colliding[0] == self.objects[3]: # Quit
                sge.game.end()

        elif button == 'left' and self.screen == 'OPTIONS':
            pass
            
    def event_step(self,tp,dt):
        self.project_sprite(self.logo,0,w//2,80,1)

class MainRoom(dsp.Room):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for obj in self.objects[:]:
            self.remove(obj)
            
        #load_game()
        dragons.extend([Dragon(w//2,h//2) for i in range(10)])
        objects = [DragonObj(z=i) for i in range(len(dragons))]
        #objects.append(Draggable(0,0,sprite=get_mate_anim(objects[8].dragon,objects[9].dragon)))
        self.objects.extend(objects)
        #save_game()
    
class Draggable(dsp.Object):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)
        # bbox = calc_bbox(self.sprite,0) # the line was long lol
        # self.bbox_x,self.bbox_y,self.bbox_width,self.bbox_height = bbox
        self.grabbing = False
        self.offx = 0
        self.offy = 0
        self.original = self.sprite.copy()
        self.transparent = self.sprite.copy()
        self.transparent.draw_rectangle(0,0,1000,1000,
                                       fill=gfx.Color((255,255,255,128)),
                                       blend_mode=sge.BLEND_RGBA_MULTIPLY)

    def event_step(self,x,y):
        if self.grabbing:
            self.x = sge.game.mouse.x+self.offx
            self.y = sge.game.mouse.y+self.offy
            
        else:
            self.sprite = self.original

    def event_mouse_button_press(self,button):
        if  button == 'left':
            if self != top_obj(Draggable,sge.game.mouse.x,sge.game.mouse.y):
                return
            self.grabbing = True
            self.offx = self.x-sge.game.mouse.x
            self.offy = self.y-sge.game.mouse.y
            self.sprite = self.transparent

    def event_mouse_button_release(self,button):
        if button == 'left':
            self.grabbing = False

class DragonObj(Draggable):
    """Internally contains a Dragon object, from which it pulls its attributes."""
    def __init__(self,dragon=None,z=0):
        self.dragon = dragon
        if self.dragon == None:
            self.dragon = Dragon(w//2,h//2)
        super().__init__(self.dragon.x,self.dragon.y,z=z,
                         sprite=get_dragon_sprite(self.dragon))

############### GAME INITIALIZATION ###############
# Create Game object
Game(width=w, height=h, fps=FPS, window_text=appname,
     scale=3, scale_method="noblur")

# Load font
font = gfx.Font(os.path.join('pixel fonts',"Quadratic.ttf"), size=13)
lfont = gfx.Font(os.path.join('pixel fonts',"Quadratic.ttf"), size=26)

# Load backgrounds
bgspr = gfx.Sprite("bubble","backgrounds",fps=FPS,origin_x=64,origin_y=64)
bglayers = [gfx.BackgroundLayer(bgspr,0,0,repeat_left=True,repeat_right=True,
                              repeat_up=True,repeat_down=True)]
background = sge.gfx.Background([], sge.gfx.Color("white"))

############### FUNCTION DEFINITIONS ###############
def save_game(num=1):
    """Writes all information required to restore a profile to the
       savefile location, given by 'appdirs' module. Also, if the file
       or write directory does not yet exist, the method will create
       them as necessary."""
    if not os.path.exists(SAVEDIR):
        os.makedirs(SAVEDIR)
    savefile = os.path.join(SAVEDIR,'file'+str(num)+'.save')
    outfile = gzip.open(savefile,'wb')
    global dragons
    global rooms
    global inventory
    global money
    global settings
    
    pickle.dump(dragons,outfile)
    pickle.dump(inventory,outfile)
    pickle.dump(money,outfile)
    pickle.dump(settings,outfile)
    outfile.close()
        
def load_game(num=1):
    '''Maybe should be called only at beginning of game?
      probably yea lol. Also only call it after saving the file haha'''
    savefile = os.path.join(SAVEDIR,'file'+str(num)+'.save')
    infile = gzip.open(savefile,'rb')
    global dragons
    global rooms
    global inventory
    global money
    global settings
    
    del dragons[:]
    del rooms[:]
    inventory.clear()
    money[0] = 0
    settings.clear()
        
    dragons.extend(pickle.load(infile))
    print(dragons)
    inventory.update(pickle.load(infile))
    money[0] = pickle.load(infile)[0]
    settings.update(pickle.load(infile))
    infile.close()

def current_fps():
    "Returns rate the game is running at in fps."
    return round(1/(sge.game.regulate_speed(None)/1000),2);

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

def draw_all_frames(base,over,x=0,y=0,blendmode=sge.BLEND_NORMAL):
    """Draws all frames of 'over' onto 'base'."""
    for f in range(base.frames):
        base.draw_sprite(over,f,x,y,frame=f,blend_mode=blendmode)

def recolor(sprite, col1, texsprite, rel):
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
    texsprite.draw_rectangle(0,0,temp.width,temp.height,fill=col1,
                             blend_mode=sge.BLEND_RGBA_MULTIPLY)
    
    # After next line, temp is now a white box with color texture overlaid
    temp.draw_sprite(texsprite,0,0,0)
    
    # Overlay result to current sprite using multiply to get rid of the white
    sprite.draw_sprite(temp,0,rel,rel,
                            blend_mode=sge.BLEND_RGB_MULTIPLY)

def overlay(sprite,col):
    """Uses RGBA Multiply to overlay 'col' onto 'sprite'."""
    sprite.draw_rectangle(0,0,sprite.width,sprite.height,fill=col,
                             blend_mode=sge.BLEND_RGBA_MULTIPLY)


def update_inventory(item, count):
    """Adds 'count' items to the inventory."""
    global inventory    
    if inventory[item] != None:
        inventory[item] += count
    else:
        inventory[item] = count

def item_value(item):
    """Returns the monetary value of the input item based on its name string."""
    if item == 'tuber': return 10
    elif item == 'cherries': return 20
    elif item == 'apple': return 20
    elif item == 'berries': return 40
    elif item == 'fish': return 100
    else: return None
    
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

def get_dragon_sprite(dragon):
        """Must be called after sge.game has been initialized.
           Returns a sprite based on the dragon's current state.
           This sprite is not saved as a part of this class because
           in order to pickle the entire list of dragons, no non-primitive
           types can be used."""

        # default void
        sprite = None
        # base colors
        pricol = Color(dragon.primary_col)
        eyecol = Color(dragon.eye_col)
        # texture sprite
        texsprite = dragon.get_texture()

        if dragon.state == 'neutral':
            sprite = Sprite("base_dragon","sprites",fps=2)
            recolor(sprite,pricol,texsprite,dragon.toffset)
            eyes = Sprite("base_eyes","sprites")
            overlay(eyes,eyecol)
            draw_all_frames(sprite,eyes,6,9)
            
        elif dragon.state == 'walking':
            pass
        
        elif dragon.state == 'sleeping':
            sprite = Sprite("dragon_sleeping","sprites",fps=1)
            recolor(sprite,pricol,texsprite,dragon.toffset+1)
            
        elif dragon.state == 'eating':
            sprite = Sprite("dragon_eating","sprites",fps=2)
            recolor(sprite,pricol,texsprite,dragon.toffset)
            eyes = Sprite("base_eyes","sprites")
            overlay(eyes,eyecol)
            draw_all_frames(sprite,eyes,4,18)
            
        elif dragon.state == 'hungry':
            pass
        elif dragon.state == 'affection':
            pass
        elif dragon.state == 'mating':
            pass

        if dragon.pregnant:
            # no sprite change?
            pass

        resize_sprite(sprite,1) # centralize
        return sprite

def get_mate_anim(dom,sub,closeup=False):
    '''FULLY IMPLEMENTED! Now just add all the animation names to the appropriate lists haha'''
    
    # autoswap to correctly select the dominant dragon.
    if dom.dominance < sub.dominance:
        dom, sub = sub, dom

    if dom.dominance == sub.dominance:
        if choice([True,False]): # 50% of the time
            dom, sub = sub, dom
    
    maledom = ['doggystyle']
    femdom = ['doggystyle'] # cowgirl, reverse cowgirl
    # lesbian = []  ? not sure if this is needed
    animchoice = ""
    
    if closeup:
        if dom.sex != sub.sex and dom.sex == 'm': # straight, dominant male
            animchoice = '' # straight doggystyle/missionary closeup
        elif dom.sex != sub.sex and dom.sex == 'f': # straight, dominant female
            animchoice = '' # straight cowgirl closeup
        elif dom.sex == sub.sex and dom.sex == 'm': # gay males
            animchoice = '' # gay doggystyle/missionary closeup
        else: # lesbians ;P
            animchoice = '' # lesbian missionary/oral closeup
    else:
        if dom.sex != sub.sex and dom.sex == 'm': # straight, dominant male
            animchoice = choice(maledom)
        elif dom.sex != sub.sex and dom.sex == 'f': # straight, dominant female
            animchoice = choice(femdom)
        elif dom.sex == sub.sex and dom.sex == 'm': # gay males
            animchoice = choice(maledom)# + "_gay" # CHECK NAME CONVENTION!
        else: # lesbians ;P
            animchoice = choice(femdom)# + "_lesbian" # not sure if it'll work like this but  we'll see

    directory = os.path.join('sprites','mating')
    matingsprite = gfx.Sprite(animchoice,directory,fps=8)
    texpath = os.path.join('sprites','tex_')
    d = Image.open(texpath+dom.texture+'.png').convert('RGBA')
    s = Image.open(texpath+sub.texture+'.png').convert('RGBA')
    domtex = d.load() # pixel data of dom texture
    subtex = s.load() # same for sub

    s1 = time()
    for i in range(len(matingsprite.rd['baseimages'])) :
        baseimg = matingsprite.rd['baseimages'][i]
        im_as_str = tostring(baseimg,"RGBA")
        img = Image.frombytes("RGBA",baseimg.get_size(),im_as_str)
        pix = img.load() # get pixel data from image for processing
        
        for j in range(img.size[0]):
            for k in range(img.size[1]): # processing pixel data...
                # replace dom color
                if pix[j,k][0] == 64: # only matches red channel.
                    if domtex[j//2,k//2][3] == 0: # darken textured areas
                        pix[j,k] = dom.primary_col
                    else:
                        l = [dom.primary_col[q]-10 for q in range(3)]
                        l.append(255)
                        pix[j,k] = tuple(l)
                # replace sub color, parallel to above 'if' block
                elif pix[j,k][0] == 128:
                    if subtex[j//2,k//2+30][3] == 0:
                        pix[j,k] = sub.primary_col                        
                    else:
                        l = [sub.primary_col[q]-10 for q in range(3)]
                        l.append(255)
                        pix[j,k] = tuple(l)
                # replace dom eyecol
                # replace sub eyecol
        # Push result back into sprite
        matingsprite.rd['baseimages'][i] = frombuffer(img.tobytes(),img.size,'RGBA')
    s2 = time()
    print(str(s2-s1)+' seconds')
    return matingsprite
