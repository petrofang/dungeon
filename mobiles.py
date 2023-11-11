#mobiles.py

from random import random
from time import sleep
from typing import Iterable
from objects import Object

DEBUG=True
def debug(message): print(f'{__name__} DEBUG:{message}') if DEBUG else None
debug(f'{DEBUG}')

class Party(list):
    from mobiles import Mobile
    def __init__(self, name:str='party', *mobile:Mobile):
        list.__init__(self)
        self.name=name
        self.append(mobile)
    
    def join(self, mobile:Mobile):
        if isinstance(mobile, Mobile):self.append(mobile)


class Mobile(Object): 
    def __init__(self, name:str='', hit_points=0, attack=0, defense=0):
        Object.__init__(self, name)
        from objects import Armor
        self.hit_points:int=hit_points
        self.name:str=name
        self.attack:int=attack
        self.defense:int=defense
        self.armor:Armor=None
        self.weapon=None
        self.dead:bool=False

    def die(self):
        if not self.dead:
            print(f'{self} hits the ground... DEAD')
            self.name=self.name + ' - (DEAD)'
            self.dead=True

    def equip_armor(self, item):
        
        from objects import Armor
        if isinstance(item, Armor):
            self.armor=item
            self.armor.equip()
        else:
            print(f'{item} is not armor, but {type(item)}')

    def __str__(self): return self.name
    
    def fight(self, other): 
        import combat
        combat.fight(self, other)

class Monster(Mobile):
    '''a simple monster constructor...'''
    def __init__(self, name:str='monster', hit_points:int=2, attack:int=1, defense:int=0):
        Mobile.__init__(self, name, hit_points, attack, defense)


                
    
