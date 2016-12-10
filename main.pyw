# Imports sge, sge.gfx, sge.dsp, and random modules, along with utility functions.
from utils import *

class Game(sge.dsp.Game):

    def event_step(self,rt,dt):
        # following line draws region main gameplay occurs in
        #self.project_rectangle(4,4,w*2//3,h*2//3,fill=gfx.Color('white'))
        bglayers[0].x += 1
        bglayers[0].y += 1
        
        pass

    def event_key_press(self, key, char):

        if key == 'f11':
            self.fullscreen = not self.fullscreen
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

w = 320 # convenience, width of window
h = 240 # convenience, height of window

# Create Game object
Game(width=w, height=h, fps=FPS, window_text="Dragon Breeder v"+str(VERSION),
     scale=4, scale_method="noblur")
mouse = sge.game.mouse


# Load font
font = gfx.Font("pixel fonts/Quadratic.ttf", size=13)
lfont = gfx.Font("pixel fonts/Quadratic.ttf", size=26)

# Load backgrounds
bgspr = gfx.Sprite("bubble","tiles",fps=FPS,origin_x=64,origin_y=64)
bglayers = [gfx.BackgroundLayer(bgspr,0,0,repeat_left=True,repeat_right=True,
                              repeat_up=True,repeat_down=True)]
background = sge.gfx.Background([], sge.gfx.Color("white"))

# Object/sprite
sprites = [gfx.Sprite("base_dragon","sprites",fps=FPS) for i in range(10)]
texsprite = gfx.Sprite("tex_stripes","sprites",fps=FPS)
for sprite in sprites:
    resize_sprite(sprite,1)

    if choice([1,2]) == 1:
        texsprite.flip()
    # recolor params
    col = desaturated_randcol(12,randint(25,100))
    colpri = col
    colsec = gfx.Color((col[0]//2,col[1]//2,col[2]//2,255))
    
    rel = randint(-texsprite.width,0)
    
    recolor(sprite,colpri,texsprite,colsec,rel)
    eyes = gfx.Sprite("base_eyes","sprites",fps=FPS)
    sprite.draw_sprite(eyes,0,0,0)
    
objects = [Draggable(w//2,h//2,z=i,sprite=sprites[i]) for i in range(10)]

# Create rooms
views = [dsp.View(0,0)]
sge.game.start_room = sge.dsp.Room(objects, views=views, background=background)

sge.game.start()
