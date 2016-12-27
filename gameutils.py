import os
import sge
import gzip
import pickle

from dragon import *
from colutils import *
from math import floor
from PIL import Image
from sge import gfx,dsp,collision
from random import randrange,randint,choice
from pygame.image import tostring, frombuffer
from appdirs import user_data_dir,user_cache_dir

VERSION = "1.0"
appname = "Dragon Breeder v"+VERSION
author = '566 Games'
SAVEDIR = user_data_dir(appname,author)

dragons = []
inventory = {'food':0,'money':0}
money = [0] # god damn python integer immutability
settings = {}
flags = {'seentutorial':False,'seenpeninfo':False} # update and maybe include this in the save later.

############### CLASS DEFINITIONS ###############
class Game(dsp.Game):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        status = load_game()
        if not status:
            pass # new game.
        w = sge.game.width
        h = sge.game.height
    
    def event_step(self,rt,dt):
        # following line draws region main gameplay occurs in
        # self.project_rectangle(4,4,256,192,fill=gfx.Color('black'))
        pass

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
            if isinstance(sge.game.current_room, MainRoom):
                LoadRoom(MenuRoom())
            if isinstance(sge.game.current_room, MenuRoom):
                self.event_close()       

    def event_close(self):
        save_game()
        self.end()

class LoadRoom(dsp.Room):
    
    def __init__(self,nextroom,tr='wipe_matrix',tt=300):
        super().__init__()
        self.next = nextroom
        framecount = ms_to_frames(tt)+2
        self.alarms.update({'nextroom':framecount})
        self.tr = tr; self.tt = tt
        self.start(transition=tr,transition_time=tt)

    def event_alarm(self,alarm_id):
        if alarm_id == 'nextroom':
            self.next.start(transition=self.tr,transition_time=self.tt)
    
class MenuRoom(dsp.Room):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for obj in self.objects[:]:
            self.remove(obj)

        # Load backgrounds
        bgspr = gfx.Sprite("bubble","backgrounds",fps=FPS,origin_x=64,origin_y=64)
        self.bglayers = [gfx.BackgroundLayer(bgspr,0,0,repeat_left=True,repeat_right=True,
                                      repeat_up=True,repeat_down=True)]
        self.background = sge.gfx.Background(self.bglayers, sge.gfx.Color("white"))
        
        self.logo = gfx.Sprite('logo','sprites')
        resize_sprite(self.logo,1)
        self.screen = 'MAIN'
        self.buttons = ['START GAME','OPTIONS','HOW TO PLAY','QUIT']
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
                LoadRoom(MainRoom(background=gfx.Background([],color=gfx.Color
                    ('white'))))
            elif colliding[0] == self.objects[1]: # Options
                pass#self.screen = 'OPTIONS'
            elif colliding[0] == self.objects[2]: # Tutorial
                pass
            elif colliding[0] == self.objects[3]: # Quit
                sge.game.end()

        elif button == 'left' and self.screen == 'OPTIONS':
            pass
            
    def event_step(self,tp,dt):
        self.project_sprite(self.logo,0,w//2,80,1)
        self.bglayers[0].x += 1
        self.bglayers[0].y += 1

class MainRoom(dsp.Room):
    
    def __init__(self,*args,**kwargs):
        
        super().__init__(*args,**kwargs)

        for obj in self.objects[:]:
            self.remove(obj)
        self.ui = gfx.Sprite('ui','sprites')
        self.ui_selected = gfx.Sprite('ui_selected','sprites')
        self.scr = gfx.Sprite(width=720,height=480)
        self.state = 'dragons'
        
        self.selected_dragon = None
        self.hold_dragon = None
        self.swapval = -1
        self.dragons_per_pen = 5
        
        self.info_text = Button(44,219,font,width=80) # Holds basic game info like stuff about selected dragon etc
        self.text_input = None # An object that can be created as a text input which appears on screen
        
        self.dragonobjects = []
        for i in range(len(dragons)):
            self.dragonobjects.append(DragonObj(dragon=dragons[i],z=i,room=self))
        self.currentpen = self.dragonobjects[0:self.dragons_per_pen] # default first five dragons

        self.buttons = [Button(310,30,text="Dragons",action=self.switch_state,params='dragons'),
                   Button(310,80,text="Lakeside",action=self.switch_state,params='lakeside'),
                   Button(310,126,text="Store",action=self.switch_state,params='store'),
                   Button(310,172,text="Forest",action=self.switch_state,params='forest'),
                   Button(310,220,text="Exit",action=LoadRoom,params=MenuRoom())]
        
        self.objects.extend(self.currentpen)
        self.objects.extend(self.buttons)
        self.objects.append(self.info_text)
        
    def event_step(self,tp,dt):

        for drobj in self.dragonobjects:
            drobj.update()
            
        # update interactions between dragons
        for i in range(len(self.dragonobjects)):
            drobj = self.dragonobjects[i]
            for j in dragons_in_same_pen(i): # guaranteed to capture all dragons in the same pen
                other = self.dragonobjects[j]
                if not drobj.interacted and drobj.dragon.facing != other.dragon.facing and \
                       drobj.collision_point() == other.collision_point():
                    drobj.interacted = other
                    other.interacted = drobj
                    ismate = drobj.interact(other)
                    if ismate:
                        drobj.mate = other
                        other.mate = drobj
                elif drobj.interacted and drobj.collision_point() == drobj.interacted.collision_point():
                    pass # changes nothing
                else:
                    drobj.interacted = False
                    
            if not drobj.dragon.mate: # if the dragon decided to break up with its current mate, set the object mate
                drobj.mate = None
                
        # ui
        self.project_sprite(self.ui,0,0,0,2)
        if self.state == 'dragons':
            self.project_sprite(self.ui_selected,0,262,10,3,blend_mode=sge.BLEND_RGBA_ADD)
        elif self.state == 'lakeside':
            self.project_sprite(self.ui_selected,0,262,57,3,blend_mode=sge.BLEND_RGBA_ADD)
        elif self.state == 'store':
            self.project_sprite(self.ui_selected,0,262,104,3,blend_mode=sge.BLEND_RGBA_ADD)
        elif self.state == 'forest':
            self.project_sprite(self.ui_selected,0,262,151,3,blend_mode=sge.BLEND_RGBA_ADD)

        # info section/lower panel buttons
        if self.state == 'dragons':
            if self.selected_dragon:
                sel = self.selected_dragon.dragon
                sx = 'MALE' if sel.sex == 'm' else 'FEMALE'
                self.info_text.update(sel.name+"\n"+sx+"/"+sel.rank)
            else:
                self.info_text.update("")
        
        # game screen
        self.scr.draw_lock()
        self.scr.draw_clear()
        if self.state == 'dragons':
            # draw dragon screen background with fence things
            for obj in self.currentpen: # draw dragons in current pen
                self.scr.draw_sprite(obj.sprite,obj.image_index,obj.x-4,obj.y-4,obj.z)
        elif self.state == 'lakeside':
            self.scr.draw_sprite(gfx.Sprite('outdoors','sprites\\ase'),0,0,0,1)
        self.scr.draw_unlock()
        self.project_sprite(self.scr,0,4,4,1)

        # finally, text input box over everything if it exists
        if self.text_input:
            ti = self.text_input
            self.project_sprite(ti.sprite,0,ti.x,ti.y,ti.z)

    def event_mouse_button_press(self,button):
        if  button == 'left':
            # manage input
            clicked = top_obj(DragonObj,sge.game.mouse.x,sge.game.mouse.y)
            if clicked and (self.selected_dragon != clicked):
                self.selected_dragon = clicked
                print(clicked.dragon.info())
                if clicked.dragon.state == 'mating':
                    pass # go to the mating scene room and display
            else:
                self.selected_dragon = None
        if button == 'right':
            # swap dragons
            clicked = top_obj(DragonObj,sge.game.mouse.x,sge.game.mouse.y)
            if clicked:
                if self.swapval >= 0:
                    if self.swap_dragons(self.swapval,self.dragonobjects.index(clicked)):
                        self.swapval = -1
                    else:
                        pass
                        # error message
                self.swapval = self.dragonobjects.index(clicked)
            else:
                self.swapval = -1
                
    def event_key_press(self,key,char):
        if self.text_input:
            self.text_input.event_key_press(key,char)
        try:
            if self.state == 'dragons':
                pennum = int(char)
                self.switch_pen(pennum)
        except ValueError:
            pass
        
    def switch_state(self,state):
        # Sets current display state and alters necessary parameters.
        if state in ('dragons','lakeside','store','forest'):
            if self.state == 'dragons' and state != 'dragons':
                self.selected_dragon = None
                self.info_text.update("")
            self.state = state
        else: print("unknown state input: %s" % state)

    def switch_pen(self,pennumber):
        # switch to display input pen
        dpp = self.dragons_per_pen

        if pennumber > get_pen_count() or pennumber < 1: return
        
        for obj in self.currentpen:
            self.remove(obj)
        
        pennumber -= 1
        start = pennumber*dpp; end = pennumber*dpp+dpp
        self.currentpen = self.dragonobjects[start:end]
        self.selected_dragon = None
        
        for drobj in self.currentpen:
            self.add(drobj)

    def swap_dragons(self,i1,i2):
        """Swaps the dragons at index i1 and i2 if they are in an acceptable state to do so and returns True else returns False."""
        if i1 >= len(self.dragonobjects) or i1 < 0 or i2 >= len(self.dragonobjects) or i2 < 0:
            # invalid index
            return False
        d1 = self.dragonobjects[i1]
        d2 = self.dragonobjects[i2]
        self.swapval = -1
        if d1.dragon.state in ('walking','neutral','eating','scratching','sleeping'):
            if d2.dragon.state in ('walking','neutral','eating','scratching','sleeping'):
                # swap and move to correct location
                self.dragonobjects[i1].dragon.x,self.dragonobjects[i2].dragon.x = self.dragonobjects[i2].dragon.x,self.dragonobjects[i1].dragon.x
                self.dragonobjects[i1],self.dragonobjects[i2] = self.dragonobjects[i2],self.dragonobjects[i1]
                return True
        return False

class Button(dsp.Object):
    """On click this button object will perform the input action with the input parameters.
       If params == None, then action is called with no arguments. The required method for
       parsing the input arguments is automatically detected and they are unpacked as
       necessary when the function is called, i.e. if type(params) == (list or tuple) then
       action is called in the following manner: action(*params). This works for most types."""
    def __init__(self,x,y,font=None,text="",width=85,height=34,action=None,params=None):
        super().__init__(x,y,z=10,tangible=False)
        if font == None:
            font = lfont
        self.sprite = gfx.Sprite(width=width,height=height)
        self.sprite.draw_text(font,text,width//2+2,height//2,halign='center',valign='middle')
        self.font = font
        self.width = width
        self.height = height
        self.sprite.origin_x=width//2;self.sprite.origin_y=height//2
        self.action = action
        self.params = params

    def update(self,text):
        self.sprite.draw_clear()
        self.sprite.draw_rectangle(0,0,self.width,self.height,fill=gfx.Color((255,255,255,200)),outline=gfx.Color('black'))
        self.sprite.draw_text(self.font,text,self.width//2+2,self.height//2,halign='center',valign='middle',color=gfx.Color('black'))

    def event_mouse_button_press(self,button):
        if  button == 'left':
            m = sge.game.mouse
            if mouse_within(self):
                if self.action and self.params:
                    # Unpack as necessary
                    if type(self.params) in (list,tuple):
                        self.action(*self.params)
                    elif type(self.params) == dict:
                        self.action(**self.params)
                    else:
                        self.action(self.params)
                elif self.action: self.action()

class TextInput(dsp.Object):
    """A text box that the user can type into. The 'action' input is a function that is called when
       the user presses Enter to submit; action should be a function that accepts a string as input"""
    def __init__(self,text="",width=250,maxlen=11,action=None):

        height = font.get_height('ASDF')+4
        # created at center of screen.
        super().__init__(x=w//2,y=h//2,z=12,visible=True,tangible=False)
        
        self.sprite = gfx.Sprite(width=width,height=height)
        self.sprite.draw_text(font,text,width//2+2,height//2,halign='center',valign='middle')
        self.width = width
        self.height = height
        resize_sprite(self.sprite,1)

        self.maxlen = maxlen
        self.action = action
        self.text = text
        self.update()

    def update(self):
        self.sprite.draw_clear()
        self.sprite.draw_rectangle(0,0,self.width,self.height,fill=gfx.Color((255,255,255,200)),outline=gfx.Color('black'))
        self.sprite.draw_text(font,self.text,2,self.height//2,halign='left',valign='middle',color=gfx.Color('black'))

    def event_key_press(self, key, char):
        if char.isalnum() or char == ' ':
            self.text += char if len(self.text) <= self.maxlen else ""
            self.update()
        elif key == 'backspace':
            self.text = self.text[:-1]
            self.update()
        elif key == 'enter':
            # submit text to action
            if self.action:
                self.action(self.text)
            self.destroy()
            del self
            sge.game.current_room.text_input = None

class Dialog(dsp.Object):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
    
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
            if self != top_obj(Draggable,sge.game.mouse.x,sge.game.mouse.y): return
            self.grabbing = True
            self.offx = self.x-sge.game.mouse.x
            self.offy = self.y-sge.game.mouse.y
            self.sprite = self.transparent

    def event_mouse_button_release(self,button):
        if button == 'left':
            self.grabbing = False

class DragonObj(dsp.Object):
    
    """Internally contains a Dragon object, from which it pulls its attributes."""
    def __init__(self,room,dragon=None,z=0):

        self.dragon = dragon if dragon else Dragon()
        super().__init__(self.dragon.x,self.dragon.y,z=z,
                         sprite=get_dragon_sprite(self.dragon),visible=False)
            
        self.room = room
        self.facing = -1
        self.drawing = True
        self.interacted = False # becomes true when this dragon interacts with another on a per-frame basis.

        self.mate = None # This is the object mate.
        # find the object corresponding to the dragon's mate and set it as the object mate
        if self.dragon.mate:
            mt = self.dragon.mate
            for d2 in self.room.dragonobjects:
                if d2.dragon.as_dict() == mt:
                    self.mate = d2
                    d2.mate = self
                    break # we're done once found

    def collision_point(self):
        """All dragons collide at front, so this method returns the x value at which this dragon will collide with something."""
        return floor(self.dragon.x)-self.sprite.width//2 if self.dragon.facing == -1 else floor(self.dragon.x)+self.sprite.width//2

    def interact(self,other):
        return self.dragon.interact(other.dragon)

    def update(self):

        # control
        initstate = self.dragon.state
        output = self.dragon.update(inventory, self.mate.dragon if self.mate != None else None)

        if output:
            if isinstance(output, Dragon):
                if len(dragons) < 20:
                    dragons.append(output)
                    self.room.dragonobjects.append(DragonObj(self.room,dragon=dragons[-1]))
                    # update dragonobjects etc
                else:
                    pass # autosell the dragon egg
            if isinstance(output, int):
                pass

        # if the dragonobject isn't visible we don't need to draw any of the following or change sprites or what have you
        if self not in self.room.currentpen:
            self.drawing = False
            return

        # To test whether or not this dragon needs to change sprites, test for a change of state or prior drawing
        # States that do not change the dragon's sprite can be filtered out.
        requiresupdate = self.dragon.state != initstate or (not self.drawing)
        if requiresupdate:
            self.sprite = get_dragon_sprite(self.dragon)
            self.z = 10 if self.dragon.state == 'mating' else 0
            self.image_fps = self.sprite.fps
            if self.facing == 1:
                self.sprite.mirror()
        
        self.x = self.dragon.x; self.y = self.dragon.y # update object position

        # if one frame has passed since the sprite was properly oriented
        if self.dragon.facing != self.facing:
            self.sprite.mirror()
            self.facing = self.dragon.facing

        self.drawing = True

############### FUNCTION DEFINITIONS ###############
def load_game(num=1):
    '''Maybe should be called only at beginning of game?
      probably yea lol. Also only call it after saving the file haha'''

    savefile = os.path.join(SAVEDIR,'file'+str(num)+'.save')
    if not os.path.exists(savefile):
        return False
    infile = gzip.open(savefile,'rb')
    global dragons
    global inventory
    global settings
    
    del dragons[:]
    inventory.clear()
    settings.clear()
        
    dragons.extend(pickle.load(infile))
    inventory.update(pickle.load(infile))
    settings.update(pickle.load(infile))
    infile.close()
    
    return True

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
    global inventory
    global settings
    
    pickle.dump(dragons,outfile)
    pickle.dump(inventory,outfile)
    pickle.dump(settings,outfile)
    outfile.close()

def current_fps():
    "Returns rate the game is running at in fps."
    return round(1/(sge.game.regulate_speed(None)/1000),2);

def ms_to_frames(ms):
    """Returns the number of frames corresponding to the input milliseconds."""
    return int(FPS*(ms/1000))

def seconds_to_frames(seconds):
    """Returns the number of frames corresponding to the input seconds."""
    return int(FPS*seconds)

def mouse_within(obj):
    # Returns 'true' if the input object's bounding rect contains the mouse.
    m = sge.game.mouse
    x = obj.x-obj.sprite.origin_x
    y = obj.y-obj.sprite.origin_y
    return m.x >= x and m.x <= x+obj.sprite.width and  \
           m.y >= y and m.y <= y+obj.sprite.height

def top_obj(obj,x,y):
    """"Finds the object of type 'obj' that has the largest z-value
        at point (x,y). Returns None if no objects collide at (x,y).
        Follows convention that if 'obj' is None, all types collide."""
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

def food_value(item):
    """Returns the number of dragon meals this item will provide based on its name string."""
    if item == 'tuber': return 1
    if item in ('cherries','apple'): return 2
    if item == 'berries': return 3
    if item == 'fish': return 10

def item_type(item):
    """Returns the type of input item."""
    if item in ('tuber','cherries','apple','berries','fish'):
        return 'food'
    # then do other things for other item types.
    
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

        # default
        sprite = Sprite("base_dragon","sprites",fps=2)
        # base colors
        pricol = Color(dragon.primary_col)
        eyecol = Color(dragon.eye_col)
        # texture sprite
        texsprite = dragon.get_texture()

        # Egg sprite
        if dragon.age == 'egg':
            sprite = gfx.Sprite(fps=2) # draw the egg sprite

        else:
            # Adult/juvenile dragon state
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
                
            elif dragon.state == 'scratching':
                sprite = Sprite("dragon_scratching","sprites",fps=2)
                recolor(sprite,pricol,texsprite,dragon.toffset)
                eyes = Sprite("dragon_scratching_eyes","sprites")
                overlay(eyes,eyecol)
                sprite.draw_sprite(eyes,0,5,11)
                
            elif dragon.state == 'affection':
                sprite = gfx.Sprite.from_text(font,'LOVE',color=gfx.Color('black'))
                
            elif dragon.state == 'mating':
                sprite = gfx.Sprite.from_text(font,'FUCKING <3',color=gfx.Color('black'))

        resize_sprite(sprite,1) # centralize
        return sprite

def get_pen_count():
    return (len(dragons)-1)//5 + 1

def dragons_in_same_pen(i):
    # based on index value. 0-4,5-9,10-14,15-20.
    retlist = []
    
    if i <= 4:
        retlist = list(range(0,min(5,len(dragons))))
    elif i <= 9:
        retlist = list(range(5,min(10,len(dragons))))
    elif i <= 14:
        retlist = list(range(10,min(15,len(dragons))))
    elif i <= 20:
        retlist = list(range(15,min(20,len(dragons))))
        
    retlist.remove(i)
    return retlist

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
    if choice((True,False)): matingsprite.mirror() # randomly flip the sprite horizontally
    return matingsprite

############### GAME INITIALIZATION ###############
# Create Game object
Game(width=w, height=h, fps=FPS, window_text=appname,
     scale=3, scale_method="noblur")

# Load font
font = gfx.Font(os.path.join('pixel fonts',"Quadratic.ttf"), size=13)
lfont = gfx.Font(os.path.join('pixel fonts',"Quadratic.ttf"), size=26)

names=("Sal","Bell","Colic","Decid","Yalo","Quantip","Python","Valence","Electrum","Silver","Gold","Platinum")
mdr = [Dragon(sex='m',rank='alpha',name=choice(names),fertility=8,dominance=8,attractedto='f') for _ in range(5)]
fdr = [Dragon(sex='f',rank='alpha',name=choice(names),fertility=8,dominance=1,attractedto='m') for _ in range(5)]
dragons = [mdr[i//2] if i%2 else fdr[i//2] for i in range(len(mdr)+len(fdr))]
#dragons = [Dragon(name=choice(names),rank='alpha',fertility=8,attractedto='b') for _ in range(10)]
