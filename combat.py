from random import random
from time import sleep
from objects import generate_armor as generate_armor
from mobiles import Mobile

DEBUG=True
def debug(message): print(f'DEBUG:{message}') if DEBUG else None
debug(f'{DEBUG} @ {__name__}')

def d20_roll(n:int=1): return n*(int(1+(random()*20//1)))

def fight(me, them):
    ''' intiate a fight against a Mobile or list of Mobiles '''
    if isinstance(them, list):
            for mobile in them:
                if isinstance(mobile, Mobile):
                    me.fight(mobile)  

    elif isinstance(them, Mobile):
        if not (them.dead or me.dead):  
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
                    armor_rating=them.armor.armor_rating
                    damage=max(0, damage - armor_rating)
                if damage <= 0:
                    print(f'a dull thud as it hits {them}\'s {them.armor}')
                else:
                    print("It's a hit!")
                    sleep(1)
                    print(f'damage = ({me.roll} + {me.attack}) - ({them.roll} + {them.defense})')
                    sleep(1)
                    if them.armor: 
                        print(f'{them}\'s{them.armor} prevents {them.armor.armor_rating} damage')
                    print(f'{damage} damage done to {them}!')
                    them.hit_points-=damage
                sleep(1)
                print(f'{them} HP remaining: {max(0, them.hit_points)}')
                sleep(1)
            else:
                print("Swing and a miss!")
    

            if them.hit_points < 1:
                them.dead=True
                print(f'the lifeless body of {them} hits the ground... dead.')
                sleep(2)
                print(f'{me} is victorious.')
                sleep(3)
                from players import PlayerCharacter 
                if isinstance(me, PlayerCharacter):
                    me.defense+=1
                    me.attack+=1
                    me.equip_armor(generate_armor())
                    print(f'{me} attack raised to {me.attack}.')
                    print(f'{me} defense raised to {me.defense}.')
                    print(f'{me} has equipped {me.armor}.')
                sleep(6)
            else:
                print(f'{them} fights back!')
                print('---------------------')
                them.fight(me)