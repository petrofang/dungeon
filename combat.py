#combat.py
from random import random
from time import sleep
from mobiles import Mobile
from dice import d
from dungeon_data import session

DEBUG=False
def debug(message): print(f'{__name__} *** DEBUG *** {message}') if DEBUG else None
debug(f'{DEBUG}')

def attack(me:Mobile, them:Mobile):
    # check if them is still a valid target (still in room)
    if not me.room==them.room:
        print(f"{them.name.capitalize()} has slipped away.")
    elif them.hp <=0:
        them.die()
    else:
        me.roll=d(20)
        them.roll=d(20)
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
                them.hp-=damage
                session.commit()
                print(f"{them.name.capitalize()} has {them.hp} hp remaining.")
                # report remaining HP, update in the Mobiles table


        else:
            print("Swing and a miss!")
        
        if killed(them): 
            from players import PlayerCharacter
            if isinstance(me, PlayerCharacter):
                me.experience += 1
                
                them.die()
                return
        else: attack(them, me)

def killed(them:Mobile) -> bool: 
    if them.hp <= 0:
        return True
    else: 
        return False