from utils import *
from time import time
from sge.gfx import Sprite,Color
from random import choice,randint

BI = 'b'
MALE = 'm'
FEMALE = 'f'
sexes = (MALE,FEMALE)
sexualities = (BI,MALE,FEMALE)
greek={'alpha':"α", 'beta': "β", 'gamma':"γ", 'delta':"δ", 'epsilon':"ε"}
ages = ('egg','juvenile','adult')
states = ('neutral','walking','sleeping','eating','hungry','sadness','affection','mating','pregnant')
textures = ('stripes','speckles')
class Dragon():

    def __eq__(self,other):
        if self is None or other is None:
            return False
        if self.secondary_col == other.secondary_col and self.name == other.name and \
           self.rank == other.rank and self.texture == other.texture:
            return True
        return False
    
    def __init__(self,x=None,y=None,name=None,sex=None,rank=None,dominance=None,attractedto=None,happiness=None,
                 parents=None,primary_col=None,eye_col=None,state='neutral',pregnant=False,age=None,fertility=None,
                 facing=None,canmate=False,texture=None,toffset=None,flip=None,mirror=None,mate=None,mate_attraction=None):
        """If this method is called with as few parameters as is permissible, the system will
           generate a fully wild dragon. 'rank' should be one of (alpha,beta,gamma). All colors
           in this class including primary, secondary and eye must are tuples and must be passed
           to gfx.Color as an argument for usage as a sprite/object color (because in order to
           pickle and save the objects properly they cannot contain other objects/pointers to objects)."""

        self.x = x; self.y = y;
        if x == None:
            self.x = randint(0,w)
        if y == None:
            self.y = randint(0,w)
                        
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
            if r <= 5:
                self.rank = greek['alpha']  # 5% chance for alpha
            elif r in range(6,25):
                self.rank = greek['beta']   # 20% chance for beta
            else:
                self.rank = greek['gamma'] # 75% chance for gamma
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
            r = randint(1,100)
            # Bi: 50%, Straight: 25%, Gay: 25%
            if r <= 50:
                self.attractedto = BI
            if 51 <= r <= 75:
                self.attractedto = MALE if self.sex == FEMALE else FEMALE   
            else:
                self.attractedto = FEMALE if self.sex == FEMALE else MALE 
        else:
            self.attractedto = attractedto
            if attractedto not in sexualities:
                print("Unknown sexuality.")

        if happiness == None:
            self.happiness = 3 # default
        else:
            self.happiness = clamp(happiness,1,8)
        
        self.parents = parents # Remains None if unspecified, random dragon parentage is nonexistent.

        if primary_col == None:
            # color based on rank.
            if self.rank == greek['alpha']:
                self.primary_col = tuple(pastel_randcol())
            elif self.rank == greek['beta']:
                self.primary_col = tuple(desaturated_randcol(55,randint(140,160)))
            elif self.rank == greek['gamma']:
                self.primary_col = tuple(desaturated_randcol(20,randint(80,100)))
        else:
            self.primary_col = primary_col

        if eye_col == None:
            self.eye_col = tuple(saturated_randcol())
        else:
            self.eye_col = tuple(eye_col)

        if state == None:
            state = states[0] # neutral
        else:
            self.state = state
            if state not in states:
                print("Unknown state input.")

        self.pregnant = pregnant
        if self.sex == 'm':
            self.pregnant = False

        if age != None:
            self.age = age
        else:
            self.age = ages[2]

        if fertility == None:
            self.fertility = randint(2,8)
        else:
            self.fertility = clamp(fertility,2,8)

        if texture == None:
            self.texture = choice(textures)
        else:
            self.texture = texture
            if texture not in textures:
                print('Unknown texture input.')

        self.canmate = canmate

        if facing == None:
            facing = choice([0,1]) # 1 is right, 0 is left
        

        # IMPORTANT: toffset to remain null because it's based on sprite size
        self.toffset = toffset # if null, remains null until sprite generator decides

        if flip == None:
            self.flip = choice([True,False])
        else: self.flip = flip

        if mirror == None:
            self.mirror = choice([True,False])
        else: self.mirror = mirror
        
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
        """Returns, on a scale of 0-some number, how attractive this dragon finds 'other'."""
        attractiveness = 0 # start out optimistically lol

        ###Additive/subtractive characteristics###
        if self.rank > other.rank:
            attractiveness += (ord(self.rank) - ord(other.rank))*2 # difference in rank, by ASCII distance
        elif self.rank == other.rank:
            attractiveness += 1
        else:
            attractiveness += ord(self.rank) - ord(other.rank)
        
        attractiveness += abs(self.dominance-other.dominance+1)//2 # favors large gaps in dominance
        attractiveness += other.fertility-2 # Normalize to lowest fertility

        ####Exclusive dependent characteristics####
        if self.sex == 'm' and self.attractedto == 'f' and other.sex == 'f':
            attractiveness += 1 # straight male additional attractedness to females

        if self.sex == 'f' and other.sex == 'm':
            if self.rank > other.rank: # this means self actually has lower rank, thank you ASCII table
                attractiveness += 2 # female additional attractedness to higher-ranked males
            else: attractiveness -= 1 # even lower attraction if the other is lower ranked haha
        
        if self.texture == other.texture:
            attractiveness += 1 # attracted to dragons of the same rough appearance

        if other.happiness >= 5:
            attractiveness += 1 # attracted to dragons with high happiness

        attractiveness = 0 if attractiveness < 0 else attractiveness # sad day

        return attractiveness

    def accept(self,other):
        """Involves a randomizer. The system will measure a number of attributes 
           and decide for 'self' if 'other' constitutes an acceptable mate. Has higher
           chance to reject on low compatibility. Called internally by propose function."""
        acc = False
        base = self.compatibility(other)
        chance = randint(0,15)
        if base >= chance:
            acc = True
        return acc

    def propose(self,other):
        """'self' tries to convice 'other' to be its mate. Returns True on success else False and
            updates the 'mate' and 'mate_attraction' attributes of both dragons as expected."""
        if (self.can_mate_with(other) and other.accept(self)):
            self.mate = other
            other.mate = self
            self.mate_attraction = self.compatibility(other)
            other.mate_attraction = other.compatibility(self)
            return True
        else:
            return False
    
    def get_sprite(self):
        """Must be called after sge.game has been initialized.
           Returns a sprite based on the dragon's current state.
           This sprite is not saved as a part of this class because
           in order to pickle the entire list of dragons, no non-primitive
           types can be used."""

        # default void
        sprite = None
        # base colors
        pricol = Color(self.primary_col)
        eyecol = Color(self.eye_col)
        # texture sprite
        texsprite = self.get_texture()

        if self.state == 'neutral':
            sprite = Sprite("base_dragon","sprites",fps=2)
            recolor(sprite,pricol,texsprite,self.toffset)
            eyes = Sprite("base_eyes","sprites")
            overlay(eyes,eyecol)
            draw_all_frames(sprite,eyes,6,9)
            
        elif self.state == 'walking':
            pass
        
        elif self.state == 'sleeping':
            sprite = Sprite("dragon_sleeping","sprites",fps=1)
            recolor(sprite,pricol,texsprite,self.toffset+1)
            
        elif self.state == 'eating':
            sprite = Sprite("dragon_eating","sprites",fps=2)
            recolor(sprite,pricol,texsprite,self.toffset)
            eyes = Sprite("base_eyes","sprites")
            overlay(eyes,eyecol)
            draw_all_frames(sprite,eyes,4,18)
            
        elif self.state == 'hungry':
            pass
        elif self.state == 'affection':
            pass
        elif self.state == 'mating':
            pass

        if self.pregnant:
            # no sprite change?
            pass

        resize_sprite(sprite,1) # centralize
        return sprite

    def get_texture(self):
        
        texsprite = Sprite("tex_"+self.texture,"sprites")

        # decide how to transform the sprite: translate, mirror, flip
        if self.toffset == None:
            self.toffset = randint(-texsprite.width//2,0)        
        if self.flip:
            texsprite.flip()
        if self.mirror:
            texsprite.mirror()

        return texsprite
    
def offspring(parent1,parent2):
    md = parent1 if parent1.sex == 'm' else parent2
    fd = parent1 if md != parent1 else parent2

def get_mate_anim(dom,sub,closeup=False):
    '''FULLY IMPLEMENTED! Now just add all the animation names to the appropriate lists haha'''
    
    # autoswap to correctly select the dominant dragon.
    if dom.dominance < sub.dominance:
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
                if pix[j,k][0] == 64:
                    pix[j,k] = dom.primary_col
                    if domtex[j//2,k//2][3] > 0:
                        pix[j,k] = tuple([clamp(q-20,0,255) for q in dom.primary_col])
                # replace sub color
                if pix[j,k][0] == 128:
                    pix[j,k] = sub.primary_col
                    if subtex[j//2,k//2][3] > 0:
                        pix[j,k] = tuple([clamp(q-20,0,255) for q in sub.primary_col])
                # replace dom eyecol
                # replace sub eyecol
        # Push result back into sprite
        matingsprite.rd['baseimages'][i] = frombuffer(img.tobytes(),img.size,'RGBA')
    s2 = time()
    print(str(s2-s1)+' seconds')
    return matingsprite
