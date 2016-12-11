from utils import *
from sge.gfx import Sprite
from random import choice,randint

BI = 'b'
MALE = 'm'
FEMALE = 'f'
sexes = (MALE,FEMALE)
sexualities = (BI,MALE,FEMALE)
greek={'alpha':"α", 'beta': "β", 'gamma':"γ", 'delta':"δ", 'epsilon':"ε"}
ages = ('egg','juvenile','adult')
states = ('neutral','walking','sleeping','eating','hungry','affection','mating','pregnant')
textures = ('stripes','speckles')
class Dragon():

    def __init__(self,name,sex=None,rank=None,dominance=None,attractedto=None,happiness=None,parents=None,
                 primary_col=None,eye_col=None,state='neutral',pregnant=False,age=None,texture=None,
                 toffset=None,flip=False,mirror=False,mate=None,mate_attraction=None):
        """If this method is called with as few parameters as is permissible, the system will
           generate a fully wild dragon. 'rank' should be one of (alpha,beta,gamma)."""
        
        if name == None:
            self.name = ""
        else:
            self.name = name

        if sex == None:
            self.sex = choice(sexes)
        else:
            self.sex = sex
            if sex not in sexes:
                print("Unknown sex.")
                
        if rank == None:
            r = randint(1,100)
            if r == 1:
                self.rank = greek['alpha']  # 1% chance for alpha
            if r in range(2,21):
                self.rank = greek['beta']   # 20% chance for beta
            else:
                self.rank = greek['gamma'] # 80% chance for gamma
        elif rank in greek.keys():
            self.rank = greek[rank]
        else:
            self.rank = None
            print("Unknown rank input.")
            
        if dominance == None:
            self.dominance = randint(1,8)
        else:
            self.dominance = clamp(dominance,1,8)

        if attractedto == None:
            self.attractedto = choice(sexualities)
        else:
            self.attractedto = attractedto
            if attractedto not in sexualities:
                print("Unknown sexuality.")

        if happiness == None:
            happiness = 3 # default
        else:
            self.happiness = clamp(happiness,1,8)
        
        self.parents = parents # Remains None if unspecified, random dragon parentage is nonexistent.

        if primary_col == None:
            # color based on rank.
            if self.rank == greek['alpha']:
                self.primary_col = saturated_randcol(value=randint(150,255))
            elif self.rank == greek['beta']:
                self.primary_col = pastel_randcol()
            elif self.rank == greek['gamma']:
                self.primary_col = desaturated_randcol(12,randint(35,100))
        else:
            self.primary_col = primary_col

        self.secondary_col = gen_secondary_col(self.primary_col)

        if eye_col == None:
            self.eye_col = saturated_randcol()
        else:
            self.eye_col = eye_col

        if state == None:
            state = states[0] # neutral
        else:
            self.state = state
            if state not in states:
                print("Unknown state input.")

        self.pregnant = pregnant
        if self.sex == 'm':
            self.pregnant = False
        
        if texture == None:
            self.texture = choice(textures)
        else:
            self.texture = texture
            if texture not in textures:
                print('Unknown texture input.')

        self.toffset = toffset # if null, remains null until sprite pull decides

        self.flip = flip
        self.mirror = mirror
        
        if age != None:
            self.age = age
        else:
            self.age = ages[2]
        
        self.mate = mate
        self.mate_attraction = mate_attraction

    def can_mate_with(self,other):
        '''Returns True if this dragon is potentially attracted to 'other'. Depends
          both on the calling dragon and 'other'. Both must have age == 'adult'.'''
        if self.age != ages[2] or other.age != ages[2]:
            return False
        if self.attractedto == 'b': # bi
            if other.attractedto == 'b' or other.attractedto == self.sex:
                return True
            
        if other.attractedto == 'b': # bi
            if self.attractedto == 'b' or self.attractedto == other.sex:
                return True

        if other.attractedto == self.sex and self.attractedto == other.sex:
            return True
        
        return False

    def compatibility(self,other):
        """Returns, on a scale of 1-8, how attractive this dragon finds 'other'."""
        attractiveness = 0 # start out optimistically lol
        attractiveness += ord(self.rank) - ord(other.rank) # difference in rank, by ASCII distance
        attractiveness += abs((self.dominance-other.dominance)//2) # favors large gaps in dominance
        attractiveness = 0 if attractiveness < 0 else attractiveness # sad day
        return attractiveness

    def is_gay():
        if self.attractedto == self.sex: return True
        else: return False

    def get_sprite(self):
        """Must be called after sge.game has been initialized.
           Returns a sprite based on the dragon's current state."""
        
        sprite = Sprite("base_dragon","sprites",fps=FPS) # default
        texsprite = self.get_texture()
        
        
        if self.toffset == None:
            self.toffset = randint(0,texsprite.width//2)
        if self.flip:
            texsprite.flip()
        if self.mirror:
            texsprite.mirror()
        
            
        if self.state == 'neutral':
            recolor(sprite,self.primary_col,texsprite,self.secondary_col,self.toffset)
            eyes = Sprite("base_eyes","sprites",fps=FPS)
            draw_all_frames(sprite,eyes,7,11)
        elif state == 'walking':
            pass
        elif self.state == 'sleeping':
            pass
        elif self.state == 'eating':
            pass
        elif self.state == 'hungry':
            pass
        elif self.state == 'affection':
            pass
        elif self.state == 'mating':
            pass

        if self.pregnant:
            # no sprite change?
            pass

        return sprite

    def get_texture(self):
        return gfx.Sprite("tex_"+self.texture,"sprites",fps=FPS)

md = Dragon(name="",sex=MALE,rank='alpha',attractedto=BI,dominance=8)
fd = Dragon(name="",sex=FEMALE,rank='gamma',attractedto=MALE,dominance=1)
