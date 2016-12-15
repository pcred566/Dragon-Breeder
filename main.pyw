# Imports sge, sge.gfx, sge.dsp, and random modules, along with utility functions.
from utils import *
from dragon import *

class Game(dsp.Game):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
    
    def event_step(self,rt,dt):
        # following line draws region main gameplay occurs in
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
            # This allows the player to still exit while the game is
            # paused, rather than having to unpause first.
            self.event_close()
        else:
            self.unpause()

    def event_paused_close(self):
        # This allows the player to still exit while the game is paused,
        # rather than having to unpause first.
        self.event_close()

class Draggable(sge.dsp.Object):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)
        #bbox = calc_bbox(self.sprite,0) # the line was long lol
        #self.bbox_x,self.bbox_y,self.bbox_width,self.bbox_height = bbox
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
            self.x = mouse.x+self.offx
            self.y = mouse.y+self.offy
            
        else:
            self.sprite = self.original

    def event_mouse_button_press(self,button):
        if  button == 'left':
            if self != top_obj(Draggable,mouse.x,mouse.y):
                return
            self.grabbing = True
            self.offx = self.x-mouse.x
            self.offy = self.y-mouse.y
            self.sprite = self.transparent

    def event_mouse_button_release(self,button):
        if button == 'left':
            self.grabbing = False

class DragonObj(Draggable):
    """Internally contains a Dragon object from which it pulls its attributes."""
    def __init__(self,dragon=None,z=0):
        self.dragon = dragon
        if self.dragon == None:
            self.dragon = Dragon(w//2,h//2)
        super().__init__(self.dragon.x,self.dragon.y,z=z,
                         sprite=self.dragon.get_sprite())

    
# Create Game object
Game(width=w, height=h, fps=FPS, window_text=appname,
     scale=3, scale_method="noblur")
mouse = sge.game.mouse


# Load font
font = gfx.Font(os.path.join('pixel fonts',"Quadratic.ttf"), size=13)
lfont = gfx.Font(os.path.join('pixel fonts',"Quadratic.ttf"), size=26)

# Load backgrounds
bgspr = gfx.Sprite("bubble","backgrounds",fps=FPS,origin_x=64,origin_y=64)
bglayers = [gfx.BackgroundLayer(bgspr,0,0,repeat_left=True,repeat_right=True,
                              repeat_up=True,repeat_down=True)]
background = sge.gfx.Background([], sge.gfx.Color("white"))

#load_game()
dragons.extend([Dragon(w//2,h//2) for i in range(10)])
objects = [DragonObj(z=i) for i in range(len(dragons))]
for obj in objects:
    pass#print(obj.dragon.rank,obj.dragon.primary_col)

objects.append(dsp.Object(0,0,sprite=get_mate_anim(objects[8].dragon,objects[9].dragon)))

#save_game()


# Create rooms
sge.game.start_room = sge.dsp.Room(objects, background=background)
sge.game.start()
