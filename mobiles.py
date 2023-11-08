#mobiles.py

from random import random
from time import sleep

DEBUG=True
def debug(message): print(f'DEBUG:{message}') if DEBUG else None
debug(f'{DEBUG} @ {__name__}')

class Mobile: 
    def __init__(self, name:str='', hit_points=0, attack=0, defense=0):
        self.hit_points=hit_points
        self.name=name
        self.attack=attack
        self.defense=defense
        self.armor=None
        self.dead=False

    def equip_armor(self, item):
        
        from objects import Armor
        if isinstance(item, Armor):
            self.armor=item
            self.armor.equip()
        else:
            print(f'{item} is not armor, but {type(item)}')

    def __str__(self): return self.name
    
    def fight(self, other): 
        from combat import fight
        fight(self, other)

class Monster(Mobile):
    def __init__(self, name:str='monster', hit_points:int=2, attack:int=1, defense:int=0):
        Mobile.__init__(self, name, hit_points, attack, defense)

class PlayerCharacter(Mobile):
    def __init__(self, name:str='adventurer', hit_points:int=100, attack=10, defense=5) -> None:
        Mobile.__init__(self, name, hit_points, attack, defense)

def d20_roll(n:int=1): return n*(int(1+(random()*20//1)))

def generate_player() -> PlayerCharacter:
    print(" --- New character generation ---")
    name='adventurer'
    _name=input(f'What is you name, {name}? > ')
    sleep(0.5)
    if _name != '': name=_name
    print(f'very well, {name}')
    player=PlayerCharacter(name)
    return player

                
    
