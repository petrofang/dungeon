from random import random
from time import sleep

def d20_roll(n:int=1): return n*(int(1+(random()*20//1)))

def fight(me, them):
  if not them.dead or me.dead:  
    me.roll=d20_roll()
    them.roll=d20_roll()
    print(f'{me} makes an attack at {them}!')
    sleep(3)
    print(f'{me}\'s attack: {me.attack}')
    print(f'{them}\'s defense: {them.defense}')
    sleep(3)
    print(f'{me}\'s d20: {me.roll}.')
    print(f'{them}\'s d20: {them.roll}')
    sleep(3)
    damage = me.roll + me.attack - them.roll - them.defense
    if damage > 0:
        if them.armor:
            armor_rating=them.armor.armor_rating
            damage=max(0, damage - armor_rating)
        if damage <= 0:
            print(f'a dull thud as it hits {them}\'s {them.armor}')
        else:
            print("It's a hit!")
            sleep(2)
            print(f'damage = ({me.roll} + {me.attack}) - ({them.roll} + {them.defense})')
            sleep(2)
            if them.armor: print(f'{them}\'s armor prevents {them.armor} damage')
            print(f'{damage} damage done to {them}!')
            them.hit_points-=damage
        sleep(2)
        print(f'{them} HP remaining: {max(0, them.hit_points)}')
        sleep(2)
    else:
        print("Swing and a miss!")
    sleep(3)

    if them.hit_points < 1:
        them.dead=True
        print(f'the lifeless body of {them} hits the ground... dead.')
        sleep(2)
        print(f'{me} is victorious.')
        sleep(3)
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
  else: print(f'{them} is aleady dead.')
