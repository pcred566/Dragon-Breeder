from PIL import Image
import time
import sge
from sge import dsp, gfx
from pygame.image import tostring,frombuffer

class Game(dsp.Game):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.spr = gfx.Sprite("mating_doggystyle","sprites",fps=8)
        tex = Image.open('sprites/tex_speckles.png').load()
        
        for i in range(len(self.spr.rd['baseimages'])):
            im = self.spr.rd['baseimages'][i]
            pil_string_image = tostring(im, "RGBA",False)
            pimg = Image.frombytes("RGBA",im.get_size(),pil_string_image)
            pix = pimg.load()
            
            # Image module method (THIS IS THE BEST AND FASTEST ONE SOMEHOW)
            for j in range(im.get_width()):
                for k in range(im.get_height()):
                    # replace dom color
                    if pix[j,k][0] == 64:
                        pix[j,k] = tex[j//2,k//2]
                    # replace sub color
                    if pix[j,k][0] == 128:
                        pix[j,k] = tex[j//2,k//2]
                    # replace dom eyecol
                    #replace sub eyecol
                        
            self.spr.rd['baseimages'][i] = frombuffer(pimg.tobytes(),im.get_size(),'RGBA')
            
        self.index = 0
        self.framecount = 0

    def event_step(self,rt,dt):
        # following line draws region main gameplay occurs in
        self.framecount = self.framecount+1 if self.framecount < 64 else 0
        if self.framecount % self.spr.fps == 0:
            self.index = self.index + 1 if self.index < 2 else 0
        self.project_sprite(self.spr,self.index,4,4)

Game(width=320, height=240, fps=60, window_text='swag',
     scale=3, scale_method="noblur")
background = sge.gfx.Background([], sge.gfx.Color("white"))
sge.game.start_room = sge.dsp.Room([], background=background)
sge.game.start()
