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
states = ('neutral','walking','sleeping','eating','scratching','affection','mating')
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
        if self.age == 'egg' or self.age == 'juvenile':
            if not self.parents: return "?????\nAGE: {}".format(self.age)
            else: return 'AGE: {}\nPARENTS: {}/{}'.format(self.age,
                         self.parents['fname'],self.parents['mname'])
                         
        if self.state == 'mating':
            return self.name + '/' + self.mate['name'] + '\n'
            
        line1 = 'NAME: ' + self.name + '{}' + 'SEX: ' + self.sex.upper()+"\n"
        line2 = 'ORIENT.: '+self.orientation() + '{}'+'RANK: '+self.rank+'\n'
        line3 = 'HAPPINESS: '+str(self.happiness)+'{}'+'AGE: '+self.age+'\n'
        line4 = ('DOMIN.: '+str(self.dominance)+'{}'+'FERTILITY: '+
                str(self.fertility))
        
        nstring = 'NAME: ' + self.name
        ostring = 'ORIENT.: ' + self.orientation()
        hstring = 'HAPPINESS: 4/8'
        dstring = 'DOMIN.: 5'
        w1 = 35
        line1 = line1.format(' '*(w1-len(line1)))
        line2 = line2.format(' '*(w1-len(line2)))
        line3 = line3.format(' '*(w1-len(line3)))
        line4 = line4.format(' '*(w1-len(line4)))
        st = line1+line2+line3+line4
        
        if self.parents:
            st += '\nPARENTS: ' + self.parents['fname'] + " / " + self.parents['mname']
        if self.mate:
            st += '\nMATE: ' + self.mate['name']
        if self.pregnant:
            st += "\nThis dragon will soon lay an egg."

        #st += '\n'+str(self.timers)

        return st

    def __init__(self,x=None,y=160,name=None,sex=None,rank=None,dominance=None,attractedto=None,happiness=None,
                 parents=None,primary_col=None,eye_col=None,state='neutral',pregnant=False,age=None,fertility=None,
                 facing=None,canmate=True,texture=None,toffset=None,flip=None,mirror=None,mate=None,mate_attraction=None):
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
            if r <= 1:
                self.rank = greek['alpha']  # 1% chance for alpha
            elif r in range(2,11):
                self.rank = greek['beta']   # 10% chance for beta
            else:
                self.rank = greek['gamma'] # 89% chance for gamma
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
            # Bi: 10%, Straight: 70%, Gay: 20%
            if r <= 10:
                self.attractedto = BI
            elif 11 <= r <= 80:
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
        # The reset_timers() function sets the dragon's timers using exactly these parameters.
        self.timers = {'neutral':0,'walking':-1,'sleeping':randint(FPS*60*10,FPS*60*20),
                       'hungry':randint(FPS*60*2,FPS*60*4),'hatch':-1,'mature':-1,
                       'canmate':0,'beginaffection':-1,'endaffection':-1,'endmating':-1,'givebirth':-1}

        if self.age == 'juvenile':
            maturetime = randint(FPS*60*1,FPS*60*3) # mature in 1-3 minutes.
            self.timers['mature'] = maturetime

        if self.age == 'egg':
            self.timers.update({'neutral':0,'hungry':randint(FPS*3,FPS*4)}) # hunger timer set to after hatch timer
            hatchtime = randint(FPS*60*1,FPS*60*3) # hatch in 1-3 minutes.
            self.timers['hatch'] = hatchtime

        self.interaction_count = 0 # if set to the name of a timer, prevents other timers from counting down
                        

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
        if other.happiness <= 2:
            attractiveness -= 1 # oop

        attractiveness = 0 if attractiveness < 0 else attractiveness # sad day

        return attractiveness

    def accept(self,other):
        """Involves a randomizer. The system will measure a number of attributes 
           and decide for 'self' if 'other' constitutes an acceptable mate. Has higher
           chance to reject on low compatibility. Called internally by propose function."""
        acc = False
        base = self.compatibility(other)
        chance = randint(0,8)
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

    def reset_timers(self):
        """Set timers back to default values. Starts by attempting to load the previous values of the timers
           if they are available, else defaults to resetting the timers using the method found in __init__."""
        
        self.timers.update({'neutral':0,'walking':-1,'sleeping':randint(FPS*60*10,FPS*60*20),
                   'hungry':randint(FPS*60*3,FPS*60*5),'hatch':-1,'mature':-1,
                   'canmate':-1,'endaffection':-1,'endmating':-1})
        

    def update(self,inventory,mate):
        """Important function. Moves the dragon around the screen and causes it to interact with other dragons.
           Returns multiple different object types depending on the dragon's actions. Also, it modifies inventory
           as necessary in order to feed the given dragon.
           Things this method can do: update the state of the input dragon, manage its timers, cause it to move.
           Things this method cannot do: change the dragon's current mate. This operation only happens via interact()."""
        
        retval = None # to return
        
        for key,val in self.timers.items():
            self.timers[key] -= 1 if val >= 0 else 0 # count down every frame
            if val == 0:
                """Possible state transitions are the following:
                   neutral->walking
                   neutral->sleeping, walking->sleeping, eating->sleeping, scratching->sleeping
                   neutral->eating/scratching, walking->eating/scratching
                   neutral->affection, walking->affection
                   affection->mating
                   mating->neutral
                """
                if key == 'neutral': # state=neutral, then walk
                    if self.state == 'mating' or self.state == 'affection':
                        # the dragons are close to each other, so we move them a space apart to prevent multiple interactions.
                        self.x += self.facing
                    self.timers['walking'] = randint(FPS*2,FPS*3)
                    if abs(self.x-240) < 30 or abs(self.x-20) < 30:
                        # too close to the wall, chance to move away
                        if choice((True,True,True,False)): self.timers['walking'] = 0
                    self.state = 'neutral'
                    
                elif key == 'walking': # state=walk, then neutralize
                    if self.state == 'neutral':
                        self.state = 'walking'
                        self.timers['neutral'] = randint(FPS*1,FPS*3)
                        if choice((True,False)): self.facing = -self.facing # random flip around
                        
                        
                elif key == 'sleeping': # state=sleep, then neutralize
                    if self.state in ('neutral','walking','eating','scratching') and not self.pregnant:
                        self.happiness += 1
                        self.state = 'sleeping'
                        self.timers['sleeping'] = randint(FPS*60*10,FPS*60*20)
                        self.timers['neutral'] = randint(FPS*45,FPS*60)
                    else: # could not go from previous state to sleep state
                        self.timers['sleeping'] = randint(FPS*2,FPS*4) # check in 2-4s
                        
                elif key == 'hungry':
                    if (self.state == 'neutral' or self.state == 'walking'):
                        if inventory['food'] > 0:
                            inventory['food'] -= 1
                            self.happiness += 1
                            self.state = 'eating'
                        else:
                            self.happiness = clamp(self.happiness-1,1,8)
                            self.state = 'scratching'
                        self.timers['hungry'] = randint(FPS*60*2,FPS*60*3) # reset hunger
                        self.timers['neutral'] = FPS*3 # eat/scratch for 3 seconds then neutralize.
                    else:
                        self.timers['hungry'] = randint(FPS*2,FPS*4) # check in 2-4s
                        
                elif key == 'hatch':
                    self.age = 'juvenile'
                    self.reset_timers()
                    retval = 'hatch'
                    self.timers['mature'] = randint(FPS*60*4,FPS*60*5) # mature in 4-5 minutes
                    
                elif key == 'mature':
                    self.age = 'adult'
                    self.canmate = True
                    # The player has won if they breed a dragon with perfect stats
                    # if self.is_perfect(): return 'victory'
                    
                elif key == 'canmate':
                    self.canmate = True
                    
                elif key == 'beginaffection':
                    # only called through the interact() method, and only on mate and self simultaneously.
                    self.state = 'affection'
                    self.timers['neutral'] = -1
                    self.timers['endaffection'] = FPS*3 # end affection in 3 seconds
                
                elif key == 'endaffection':
                    conditionsmet = True
                    chance = self.fertility + mate.fertility # max 16
                    matingduration = randint(FPS*30,FPS*45) # 30-45 seconds
                    # note that the above line should always find the pregnant female and should prevent mating in both mate and self.
                    
                    if 0 < self.timers['givebirth'] < matingduration or 0 < mate.timers['givebirth'] < matingduration:
                        # the female would give birth during mating in this case.
                        conditionsmet = False
                    if (not self.canmate) or (not mate.canmate): # the dragons mated too recently.
                        conditionsmet = False
                    if chance < randint(2,18): # fertility/randomness prevented the dragons from mating.
                        conditionsmet = False
                    if mate.timers['neutral'] == 0:# mate failed for some reason or another.
                        conditionsmet = False

                    if conditionsmet or mate.state == 'mating': # the dragons can mate. mate check is to prevent double chance filtration.
                        self.state = 'mating'
                        self.happiness += 1 if choice((True,False)) else 0
                        # no matter what, self and mate should always end mating simutaneously.
                        if mate.timers['endmating'] > 0:
                            self.timers['endmating'] = mate.timers['endmating']
                        else:
                            self.timers['endmating'] = matingduration
                            
                    else: # conditions not met, revert to a normal state
                        self.timers['neutral'] = 0
                        mate.timers['neutral'] = 0
                            
                elif key == 'endmating':
                    if self.sex == FEMALE and mate.sex == MALE and not self.pregnant: # chance to get pregnant~
                        chance = self.fertility*2+mate.fertility//2
                        if chance >= randint(2,18):
                            self.pregnant = True
                            self.timers['givebirth'] = randint(FPS*60*5,FPS*60*7) # 5-7 minutes
                    self.canmate = False
                    self.timers['canmate'] = randint(FPS*60,FPS*90) # 1-1.5 minute rest period
                    self.timers['neutral'] = 0
                
                elif key == 'givebirth':
                    retval = offspring(self,mate)
                    self.pregnant = False


        if self.age == 'egg':
            pass # do nothing

        elif self.state == 'walking':
            speed = 0.6 # pixels per frame
            self.x += speed*self.facing
            if self.x+speed*self.facing < 20 or self.x+speed*self.facing > 240:
                self.facing = -1 if self.facing == 1 else 1
            # pop that nigga back into the room if he trynna cut
            if self.x > 240:
                self.x = 240
            if self.x < 20:
                self.x = 20

        if self.age == 'adult' and self.mate == None:
            self.canmate = True

        return retval

    def interact(self,mate,other,other_mate):
        """'self' and 'other' will interact. If the dragon has a mate, the 'mate' parameter is the dragon's mate and
           the other_mate parameter is other's mate, if said mates exist. This function is capable of modifying all
           of its input parameters; for example, if self and other decide to become mates that will happen in this function,
           and if, for example, other decides to break up with its mate, then that will also occur here."""
        
        if self.state not in ('walking','neutral') or self.age != 'adult':
            # no interaction possible during these conditions, as the dragon is either unable to or is already interacting.
            return False

        if other and (other.state not in ('walking','neutral') or other.age != 'adult'):
            # same as above, but with other
            return False
        
        retval = ""
        if self and self.mate: # self has a mate
            self.interaction_count += 1
        if other and other.mate: # other has a mate
            other.interaction_count += 1
        
        if not self.mate and other:
            if choice((True,True,True,False)): # 75% chance to interact
                if other.mate:
                    return # only messes with single dragons
                if self.can_mate_with(other) and self.accept(other):
                    if self.propose(other):
                        self.timers['beginaffection'] = other.timers['beginaffection'] = 0
                        self.interaction_count = other.interaction_count = 0
                        retval = 'mated'

        if self.mate and other == mate:
            "This if block affects both self AND other (and other == mate)."
            # interact with mate
            self.interaction_count = other.interaction_count = 0
            chance = 80 if (self.canmate and other.canmate) else 33
            chance = 15 if self.happiness + mate.happiness < randint(3,14) else chance
            if chance >= randint(1,100):
                self.timers['beginaffection'] = mate.timers['beginaffection'] = 0 # the loving mood ensues

        if self and self.mate and other != mate: # other is not this dragon's mate
            "This if block affects only self."
            if other and not other.mate and self.compatibility(other) > self.mate_attraction: #  other has no mate
                if self.breakup_with_current_and_remate(mate,other):
                    retval = 'breakup_remate_self_other'
            if self.interaction_count >= 50: # the dragon and its mate have not found each other in a long ass time
                if low_mate_interaction_reevaluate(self,mate):
                    retval = 'breakup'

        if other and other.mate and self != other_mate: # other has a mate which is not self
            "This if block is a duplicate of the second one in the above block, but rather affects other."
            if self and not self.mate and other.compatibility(self) > other.mate_attraction: #  self has no mate
                if other.breakup_with_current_and_remate(other_mate,self):
                    retval = 'breakup_remate_other_self'
            if other.interaction_count >= 50: # other and its mate have not found each other in a long ass time
                if low_mate_interaction_reevaluate(other,other_mate):
                    retval = 'other_breakup'

        return retval

    def breakup_with_current_and_remate(self,mate,other):
        
        if choice((True,True,False)) and not self.pregnant and not mate.pregnant and \
                not other.mate and self.can_mate_with(other) and self.accept(other):
            if self.propose(other):
                print('BREAKUP: {0} AND {1}, {0} REMATED {2}'.format(
                                        self.name,mate.name,other.name))
                mate.mate = None # end relationship for mate
                mate.happiness = clamp(mate.happiness-1,1,8)
                self.timers['beginaffection'] = other.timers['beginaffection'] = 0
                self.interaction_count = mate.interaction_count = other.interaction_count = 0
                return True

def low_mate_interaction_reevaluate(self,mate):
    """This function causes 'self' and 'mate' to break up if they haven't interacted in a long time."""
    self.interaction_count = 0 # reset
    self.happiness = clamp(self.happiness-2,1,8)
    if self.pregnant or mate.pregnant:
        return False # breakup is impossible if the female is pregnant
    if not(self.accept(mate) and mate.accept(self)) or 5 == randint(1,50): # chance to break
        print('BREAKUP: {} AND {}.'.format(self.mate['name'],mate.mate['name']))
        self.mate = mate.mate = None
        self.interaction_count = mate.interaction_count = 0
        return True
        
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
            if rand <= 2: # 2%
                rank = greek['alpha']
            elif rand > 2 and rand <= 12: # 10%
                rank = greek['beta']
            else: # 78%, #rekt
                rank = greek['gamma']
        elif greek['beta'] in ranks: # one beta, one gamma
            if rand <= 5: # 5%
                rank = greek['alpha']
            elif rand > 5 and rand <= 25: # 20%
                rank = greek['beta']
            else: # 50%
                rank = greek['gamma']
        elif greek['alpha'] in ranks: # one gamma, one alpha
            if rand <= 10: # 10%
                rank = greek['alpha']
            elif rand > 10 and rand <= 35: # 25%
                rank = greek['beta']
            else: # 50%
                rank = greek['gamma']
                
    elif greek['beta'] in ranks: # at most 1 gamma
        if ranks[0] == greek['beta'] and ranks[1] == greek['beta']: # 2 betas
            if rand <= 10: # 10%
                rank = greek['alpha']
            elif rand > 10 and rand <= 40: # 30%
                rank = greek['beta']
            else:
                rank = greek['gamma']
        elif greek['alpha'] in ranks: # one beta, one alpha
            if rand <= 10:
                rank = greek['alpha']
            elif rand > 10 and rand <= 50: # 40% chance for beta
                rank = greek['beta']
            else:
                rank = greek['gamma']

    else: # TWO ALPHAS
        if rand <= 20: # 20%
            rank = greek['alpha']
        elif rand > 20 and rand <= 70: # 50%
            rank = greek['beta']
        else: # 20% (#REKT LMFAO)
            rank = greek['gamma']

    ##### end rank determination block #####

    unlucky = (True,True,False) if choice((True,False)) else (True,False,False,False) # EVEN YOUR LUCK HAS LUCK
    
    if sex == 'm':
        dominance = randint(md.dominance,8)
        fertility = randint(md.fertility,8)
        
    else: # sex == 'f'
        dominance = randint(1,fd.dominance)
        fertility = randint(fd.fertility,8)

    if choice(unlucky):
        dominance -= 1
        if choice(unlucky):
            dominance -= 1

    if choice(unlucky):
        fertility -= 1
        if choice(unlucky): # holy god
            fertility -= 1

    parents = {'fcolor':md.primary_col,'mcolor':fd.primary_col,'ftexture':fd.texture,'mtexture':md.texture,
               'fname':md.name,'mname':fd.name,'feyecol':md.eye_col,'meyecol':fd.eye_col}
    
    primary_col = None # default if mother and father have no known parents, random engine will decide
    texture = choice((md.texture,fd.texture)) # default choose between texture of parents if grandparents not known

    if md.parents or fd.parents:
        if md.parents and fd.parents:
            # Choose out of grandparent colors if possible
            texture = choice((md.parents['ftexture'],md.parents['mtexture'],
                                fd.parents['ftexture'],fd.parents['mtexture']))
            eye_col = choice((md.parents['feyecol'],md.parents['meyecol'],
                                fd.parents['feyecol'],fd.parents['meyecol']))
        else:
            gp = md.parents if md.parents else fd.parents # else select existing grandparents
            texture = choice((gp['ftexture'],gp['mtexture'])) # and a texture.
            eye_col = choice((gp['feyecol'],gp['meyecol'])) # and a texture.
    
    child = Dragon(sex=sex,rank=rank,dominance=dominance,fertility=fertility,happiness=5,
                        eye_col=eye_col,parents=parents,primary_col=primary_col,age='egg')
    return child