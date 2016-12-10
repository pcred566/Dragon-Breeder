from utils import recolor
from sge.gfx import Color,Sprite
from random import choice,randint

BI = 'b'
MALE = 'm'
FEMALE = 'f'
sexes = (MALE,FEMALE)
sexualities = (BI,MALE,FEMALE)
greek="αβγδε"
ages = ('egg','juvenile','adult')
states = ('neutral','sleeping','eating','hungry','affection','mating','pregnant','dragging')
class Dragon():

    def __init__(self,name,sex,rank,dominance=None,attractedto=None,happiness=None,
                 parents=None,primary_col=None,secondary_col=None,eye_col=None,state='neutral',
                 texture=None,toffset=None,age=None,mate=None,mate_attraction=None):
        self.name = name
        
        self.sex = sex
        if sex not in sexes:
            print("Unknown sex.")
            
        self.rank = rank
        if rank not in greek:
            print("Unknown rank input.")
            
        if dominance:
            self.dominance = dominance
        else:
            self.dominance = randint(1,8)
            
        self.attractedto = attractedto
        if attractedto not in sexualities:
            print("Unknown sexuality.")

        if happiness == None:
            happiness = 3 # default
        else:
            self.happiness = happiness if happiness in range(1,9) else \
                             1 if happiness < 1 else 8 if happiness > 8 else 1
        
        self.parents = parents # Remains None if unspecified, random dragon parentage is nonexistent.
        
        self.primary_col = primary_col
        self.secondary_col = secondary_col
        self.eye_col = eye_col
        
        self.state = state
        if state not in states:
            print("Unknown state input.")
            
        self.texture = texture
        self.age = age
        self.mate = mate
        self.mate_attraction = mate_attraction

    def can_mate_with(self,other):
        '''Returns True if this dragon is potentially attracted to 'other'.
          Depends both on the calling dragon and 'other'.'''
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
        attractiveness = 8 # start out optimistically lol
        attractiveness -= ord(self.rank) - ord(other.rank) # difference in rank
        attractiveness += 0
        attractiveness = 1 if attractiveness < 1 else attractiveness
        return attractiveness

md = Dragon("",sex=MALE,rank=greek[0],attractedto=BI)
fd = Dragon("",FEMALE,greek[3],attractedto=MALE)

print (md.compatibility(fd))
