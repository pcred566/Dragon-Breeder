from time import time
from colutils import *
from random import random

BI = 'b'
MALE = 'm'
FEMALE = 'f'
sexes = (MALE,FEMALE)
sexualities = (BI,MALE,FEMALE)
greek={'alpha':"α", 'beta': "β", 'gamma':"γ", 'delta':"δ", 'epsilon':"ε"}
ages = ('egg','juvenile','adult')
states = ('neutral','walking','sleeping','eating','scratching','sadness','affection','mating')
textures = ('stripes','speckles')
class Dragon():
    """Class that contains an implementation of a dragon."""
    
    def __eq__(self,other):
        '''You can iterate through a list of dragons and do a basic test for equality using the == operator.
          The chances of all of the checked categories being equal for two input dragons that are not actually the
          same are incredibly low, however it should be noted that however slight the chance it is still possible.'''
        if self is None or other is None:
            return False
        if self.primary_col == other.primary_col and self.name == other.name and self.mirror == other.mirror and\
           self.rank == other.rank and self.texture == other.texture and self.fertility == other.fertility and    \
           self.toffset == other.toffset and self.eye_col == other.eye_col and self.dominance == other.dominance:
            return True
        return False

    def copy(self):
        """Returns an exact (deep) copy of a given dragon."""
        d = Dragon()
        for varname,varval in vars(self).items():
            setattr(d,varname,varval)
        return d

    def as_dict(self):
        """Returns a dict containing the dragon's defining characteristics. None of these are expected to change
           over the lifetime of a dragon, so the output dict can be used for comparison with a real dragon object."""
        return {'name':self.name,'sex':self.sex,'rank':self.rank,'dominance':self.dominance,'fertility':self.fertility,
                'primary_col':self.primary_col,'eye_col':self.eye_col,'texture':self.texture,'toffset':self.toffset}

    def setname(self,name):
        if isinstance(name,str):
            if len(name) >= 1:
                self.name = name
                return True
        return False

    def orientation(self):
        # prints the sexual orientation of the given dragon
        if self.attractedto == BI:
            return 'BISEXUAL'
        elif self.attractedto == self.sex:
            return 'GAY'
        else:
            return 'STRAIGHT'

    def info(self):
        """Returns a string that properly lists a dragon's stats for display purposes."""
        st = ("NAME: {}    SEX: {}\n"
            "RANK: {}     ORIENTATION: {}\n"
            "HAPPINESS: {}/8 AGE: {}\n"
            "MATE: {}").format(self.name,'MALE' if self.sex=='m' else 'FEMALE',self.rank,self.orientation(),
                                   self.happiness,self.age,self.mate['name'] if self.mate else "NONE")
        if self.parents:
            st += '\nPARENTS: ' + self.parents['fname'] + " / " + self.parents['mname']
        if self.pregnant:
            st += "\nThis dragon will soon lay an egg."
        st += '\n'+self.state
        st += '\n'+str(self.timers)

        return st

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
            self.x = randint(20,236)
        if y == None:
            self.y = 160 # HEIGHT RELATIVE TO GROUND PLANE IN VIEW THING
                        
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
        elif rank in greek.values():
            self.rank = rank
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
            elif 51 <= r <= 75:
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
        if self.sex == MALE:
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
            self.facing = choice([-1,1]) # 1 is left, -1 is right
        else: self.facing = facing
        

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
        
        # First eating begins in 2-5 minutes, sleep begins in 10-20. Begins in neutral state.
        self.timers = {'neutral':0,'walking':-1,'sleeping':randint(FPS*60*10,FPS*60*20),
                       'hungry':randint(FPS*60*2,FPS*60*5),'hatch':-1,'mature':-1,
                       'canmate':0,'endaffection':-1,'endmating':-1,'givebirth':-1}

        if self.age == 'juvenile':
            maturetime = randint(FPS*60*1,FPS*60*3) # mature in 1-3 minutes.
            self.timers['mature'] = maturetime

        if self.age == 'egg':
            hatchtime = randint(FPS*60*2,FPS*60*3) # hatch in 2-3 minutes.
            self.timers['hatch'] = hatchtime

        self.temptimers={}
                        

    def can_mate_with(self,other):
        '''Returns True if this dragon is potentially attracted to 'other'. Depends
          both on the calling dragon and 'other'. Both must have age == 'adult'.'''
        if self.age != ages[2] or other.age != ages[2]:
            return False
        
        if self.attractedto == BI: # self is bisexual
            if other.attractedto == BI or other.attractedto == self.sex:
                return True
            
        if other.attractedto == BI: # other is bisexual
            if self.attractedto == BI or self.attractedto == other.sex:
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
            else: attractiveness -= 1 # even lower attraction if the other is lower ranked haha rekt
        
        if self.texture == other.texture:
            attractiveness += 1 # attracted to dragons of the same general appearance

        if other.happiness >= 5:
            attractiveness += 1 # attracted to dragons with high happiness

        attractiveness = 0 if attractiveness < 0 else attractiveness # sad day

        return attractiveness

    def accept(self,other):
        """Involves a randomizer. The system will measure a number of attributes 
           and decide for 'self' if 'other' constitutes an acceptable mate. Has higher
           chance to reject on low compatibility. Called internally by propose function."""
        acc = False
        if self.mate:
            return False
        base = self.compatibility(other)
        chance = randint(0,7)
        if base >= chance:
            acc = True
        return acc

    def propose(self,other):
        """'self' tries to convice 'other' to be its mate. Returns True on success else False and
            updates the 'mate' and 'mate_attraction' attributes of both dragons as expected."""
        if (self.can_mate_with(other) and other.accept(self)):
            self.mate = other.as_dict()
            other.mate = self.as_dict()
            self.mate_attraction = self.compatibility(other)
            other.mate_attraction = other.compatibility(self)
            print(self.mate)
            return True
        else:
            return False

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

    def kill_timers(self):
        """Set all timers to -1."""
        self.temptimers.update({k:v for k,v in self.timers.items()})
        for key in self.timers.keys():
            self.timers[key] = -1
        return

    def revive_timers(self):
        """Set timers back to default values. Starts by attempting to load the previous values of the timers
           if they are available, else defaults to resetting the timers using the method found in __init__."""
        if self.temptimers:
            self.timers.update({k:v for k,v in self.temptimers.items()})
        else:
            self.timers.update({'neutral':0,'walking':-1,'sleeping':randint(FPS*60*10,FPS*60*20),
                       'hungry':randint(FPS*60*2,FPS*60*5),'hatch':-1,'mature':-1,
                       'canmate':-1,'endaffection':-1,'endmating':-1})
            print('something fucked up in timers')
        

    def update(self,inventory,mate):
        """Important function. Moves the dragon around the screen and causes it to interact with other dragons.
           Returns multiple different object types depending on the dragon's actions. Also, it modifies inventory
           as necessary in order to feed the given dragon."""
        
        speed = random()*3+0.2 # pixels per frame
        retval = None # to return
        
        for key,val in self.timers.items():
            
            self.timers[key] -= 1 if val >= 0 else 0 # count down every frame
            # Timer is left at -1 until it is needed again, so that it is only activated once when it reaches zero.
            if val == 0:
                # Block of events that occur when a timer reaches zero, only happens once each time a value reaches zero.
                
                if self.age == 'adult' or self.age == 'juvenile':
                    if key == 'neutral': # all states can transition to neutral
                        self.timers['walking'] = randint(FPS*1,FPS*3) # between 1 and 3 seconds
                        if choice((True,False)): self.facing = -self.facing
                        self.state = 'neutral'
                        
                    elif key == 'walking' and self.state == 'neutral': # only neutral state transition to walking
                        self.timers['neutral'] = randint(10,FPS*3) # between 10 frames and 3 seconds
                        if choice((True,False)): self.facing = -self.facing
                        self.state = 'walking'
                        
                    elif key == 'hungry':
                        if self.state in ('eating','scratching','mating','affection'):
                            self.timers['hungry'] = FPS*2 # if not in transferrable state check again in 2 s
                        self.timers['hungry'] = randint(FPS*60*2,FPS*60*4) # reset hunger timer
                        self.timers['neutral'] = FPS*4 # eat for 2 seconds then revert to neutral state
                        if inventory['food'] > 0:
                            self.happiness = clamp(self.happiness+1,1,8)
                            inventory['food'] -= 1 # this affects the actual inventory object lol
                            self.state = 'eating'
                        else: # no food in inventory
                            self.happiness = clamp(self.happiness-1,1,8)
                            self.state = 'scratching'
                            
                    elif key == 'sleeping':
                        if self.state in ('eating','scratching','mating','affection'):
                            self.timers['sleeping'] = FPS*2 # check again in 2s
                        else:
                            self.state = 'sleeping'
                            self.timers['neutral'] = randint(FPS*30,FPS*120) # wake up between 30 seconds and 2 minutes from now
                            self.timers['sleeping'] = randint(FPS*60*10,FPS*60*20) # go to sleep 10-20 minutes from now
                            retval = None
                            
                    elif key == 'canmate':
                        self.canmate = True
                        
                    elif key == 'endaffection':
                        # see if the dragons can mate
                        assert mate, self.mate
                        if self.canmate and mate.canmate:
                            chance = self.fertility + mate.fertility # 16 is max fertility
                            if chance >= choice(range(16)): # success
                                if self.timers['endmating'] < 0:
                                    self.timers['endmating'] = mate.timers['endmating'] = randint(FPS*20,FPS*35)
                                self.state = 'mating'
                                self.happiness = clamp(self.happiness+1,1,8)
                        if self.state != 'mating': # if not mating revert to old state.
                            self.revive_timers()
                            self.timers['neutral'] = 10
                            
                    elif key == 'endmating':
                        if self.sex == FEMALE and mate.sex == MALE:
                            chance = self.fertility * 2 # 16 is once again max
                            if chance >= choice(range(2,15)):
                                self.pregnant = True
                                self.timers['givebirth'] = randint(FPS*90,FPS*60*2) # give birth in 1.5-2 minutes
                        self.canmate = False
                        self.revive_timers()
                        self.timers['canmate'] = randint(FPS*10,FPS*20) # a 10-20 second rest period lmfao
                        self.timers['neutral'] = 10

                    elif key == 'givebirth':
                        print('a dragon gave birth.')
                        retval = offspring(self,mate) if mate else None
                        
                if self.age == 'juvenile':
                    if key == 'mature':
                        self.age = 'adult'
                        
                if self.age == 'egg':
                    if key == 'hatch':
                        self.age = 'juvenile'
                        self.revive_timers()
                        self.timers['mature'] = randint(FPS*60*1,FPS*60*3) # mature in 1-3 minutes
        
        if self.state == 'neutral' or self.state == 'sleeping':
            # do nothing
            pass

        elif self.state == 'walking':
            self.x += speed*self.facing
            if self.x+speed*self.facing < 20 or self.x+speed*self.facing > 240:
                self.facing = -1 if self.facing == 1 else 1
            # pop that nigga back into the room if he trynna cut
            if self.x > 240:
                self.x = 240
            if self.x < 20:
                self.x = 20
                
        return retval

    def interact(self,other):
        # The two dragons will interact.
        if self.state in ('affection','mating','sleeping','eating','scratching'):
            # no interaction possible during these states, as the dragon is either unable to or is already interacting.
            return False
        
        if not self.mate:
            if choice((True,True,True,False)): # 75% chance to interact
                if other.mate:
                    return
                if self.can_mate_with(other) and self.accept(other):
                    return self.propose(other)
            else:
                return False # nothing happened

        elif self.mate:
            if other.as_dict() == self.mate: # interact with mate
                if choice((True,True,True,True,False)): # 80% chance to interact
                    self.state = 'affection'; other.state = 'affection' # the loving mood ensues
                    # since we don't want anything happening while these dragons are doin it haha
                    self.kill_timers(); other.kill_timers()
                    self.timers['endaffection'] = other.timers['endaffection'] = FPS*3 # end in 3 seconds then chance to mate
        return False

def offspring(parent1,parent2):
    
    """Returns the offspring of the two input dragons as an egg."""
    md = parent1 if parent1.sex == 'm' else parent2
    fd = parent1 if md != parent1 else parent2
    ranks = (md.rank,fd.rank)

    sex = choice(sexes)
    
    ##### start rank determination block #####
    
    rand = randint(1,100) # percent.
    if greek['gamma'] in ranks:
        if ranks[0] == greek['gamma'] and ranks[1] == greek['gamma']: # 2 gammas
            if rand <= 10: # 10%
                rank = greek['alpha']
            elif rand > 10 and rand <= 40: # 30%
                rank = greeek['beta']
            else: # 60%, #rekt
                rank = greek['gamma']
        elif greek['beta'] in ranks: # one beta, one gamma
            if rand <= 10: # 10%
                rank = greek['alpha']
            elif rand > 10 and rand <= 50: # 40%
                rank = greek['beta']
            else: # 50%
                rank = greek['gamma']
        elif greek['alpha'] in ranks: # one beta, one alpha
            if rand <= 20: # 20%
                rank = greek['alpha']
            elif rand > 20 and rand <= 50: # 30%
                rank = greek['beta']
            else: # 50%
                rank = greek['gamma']
                
    elif greek['beta'] in ranks:
        if ranks[0] == greek['beta'] and ranks[1] == greek['beta']: # 2 betas
            if rand <= 10: # 20%
                rank = greek['alpha']
            elif rand > 10 and rand <= 40: # 30%
                rank = greeek['beta']
            else: # 60% chance for another gamma, #rekt
                rank = greek['gamma']
        elif greek['alpha'] in ranks: # one beta, one alpha
            if rand <= 10:
                rank = greek['alpha']
            elif rand > 10 and rand <= 50: # 40% chance for beta
                rank = greek['beta']
            else:
                rank = greek['gamma']

    else: # TWO ALPHAS
        if rand <= 50: # 50%
            rank = greek['alpha']
        elif rand > 50 and rand <= 90: # 40%
            rank = greek['beta']
        else: # 10% (#REKT LMFAO)
            rank = greek['gamma']

    ##### end rank determination block #####

    unlucky = [True,True,False] if choice((True,False)) else [True,False] # EVEN YOUR LUCK HAS LUCK
    
    if sex == 'm':
        dominance = randint(md.dominance,8)
        if choice(unlucky):
            dominance -= 1
        fertility = randint(md.fertility,8)
        
    else: # sex == 'f'
        dominance = randint(1,fd.dominance)
        if choice(unlucky):
            dominance += 1
        fertility = randint(fd.fertility,8)
        
    if choice(unlucky):
        fertility -= 1

    parents = {'fcolor':md.primary_col,'mcolor':fd.primary_col,'ftexture':fd.texture,'mtexture':md.texture,
               'fname':md.name,'mname':fd.name}
    
    primary_col = None # default if mother and father have no known parents, random engine will decide
    texture = choice(md.texture,fd.texture) # default choose between texture of parents if grandparents not known
    if md.parents or fd.parents:
        if md.parents and fd.parents:
            # Choose out of grandparent colors if possible
            primary_col = choice((md.parents['fcolor'],md.parents['mcolor'],fd.parents['fcolor'],fd.parents['mcolor']))
            texture = choice((md.parents['ftexture'],md.parents['mtexture'],fd.parents['ftexture'],fd.parents['mtexture']))
        else:
            gp = md.parents if md.parents else fd.parents # else select existing grandparents
            primary_col = choice((gp['fcolor'],gp['mcolor'])) # and pick a color...
            texture = choice((gp['ftexture'],gp['mtexture'])) # and a texture.
    
    child = Dragon(sex=sex,rank=rank,dominance=dominance,fertility=fertility,happiness=5,
                                          parents=parents,primary_col=primary_col,age='egg')
    return child
