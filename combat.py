#combat.py
from random import random
from time import sleep
from mobiles import Mobile

DEBUG=False
INFO=False
def debug(message): print(f'{__name__} DEBUG: {message}') if DEBUG else None
def info(message):  print(f'{__name__} INFO: {message}')  if INFO  else None
debug(f'{DEBUG}')
info(f'{INFO}')

def d20_roll(n:int=1): return n*(int(1+(random()*20//1)))

def attack(me:Mobile, them:Mobile):
    # TODO: attack as a mobile object method.
        if them.dead:
        #    debug(f'*** {{them}} {them} is dead... should not be attacking them')
        #    raise RuntimeError(them) # they shouldn't get this far? or do we just skip?
            pass

        elif me.dead:
            debug(f'*** {{me}} {me} is dead... me should not be attacking.')
            raise RuntimeError(me) # this definitely shouldn't be possible   
          
        else:
            me.roll=d20_roll()
            them.roll=d20_roll()
            print(f'{me} makes an attack at {them}!')
            sleep(2)
            print(f'{me}\'s attack: {me.attack}')
            print(f'{them}\'s defense: {them.defense}')
            sleep(1)
            print(f'{me}\'s d20: {me.roll}.')
            print(f'{them}\'s d20: {them.roll}')
            sleep(2)
            damage = me.roll + me.attack - them.roll - them.defense
            if damage > 0:
                if them.armor:
                    armor_rating=them.armor.rating
                    damage=max(0, damage - armor_rating)
                if damage <= 0:
                    print(f'a dull thud as it hits {them}\'s {them.armor}')
                else:
                    print("It's a hit!")
                    sleep(1)
                    print(f'damage = ({me.roll} + {me.attack}) - ({them.roll} + {them.defense})')
                    sleep(1)
                    if them.armor: 
                        print(f'{them.name.capitalize()}\'s {them.armor} prevents {them.armor.rating} damage')
                    print(f'{damage} damage done to {them}!')
                    them.hit_points-=damage
            else:
                print("Swing and a miss!")
            
            if killed(them): 
                from players import PlayerCharacter
                if isinstance(me, PlayerCharacter):
                    me.level_up() 
            else: fight(them, me)
    
def fight(me, them) -> Mobile:
    ''' intiate a fight against a Mobile or list of Mobiles '''  
    #TODO: handle grouping better... 
    #IDEA: a "party" iterative object representing a group of Mobiles

    if isinstance(me, list):  # PARTY COMBAT NOT IMPLEMENTED
        raise NotImplementedError(me)
        return     
        for mobile in me:
            if len(me)==1: 
                debug(f'CONDENSING LIST: {me} only has 1 member left: {mobile}')
                me=mobile
            if isinstance(mobile, (Mobile)):
                fight(mobile, them) 
            else: 
                debug(f'{mobile} is not a {Mobile}')
                raise TypeError(mobile)
            
    if isinstance(them, list):
        for each_mobile in them:
            if isinstance(each_mobile, Mobile):
                fight(me, each_mobile)
            
    elif isinstance(me, Mobile) and isinstance(them, Mobile):
        attack(me, them)

def killed(them:Mobile) -> bool: 
    ''' them.die() if sub-zero hp. returns True|False for them.dead'''
    if them.dead:
        return True
    if them.hit_points <= 0:
        them.die()
        return True
    else: 
        return False