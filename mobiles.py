#mobiles.py

from random import random
from time import sleep
from typing import Sequence, List
from objects import Object,Armor,Weapon

DEBUG=True
def debug(message): print(f'{__name__} DEBUG:{message}') if DEBUG else None
debug(f'{DEBUG}')

class Mobile(Object): 
    def __init__(self, name:str='', hit_points=0, attack=0, defense=0):
        super().__init__(name)
        self.hit_points:int=hit_points
        self.name:str=name
        self.attack:int=attack
        self.defense:int=defense
        self.armor:Armor=None
        self.weapon:Weapon=None
        self.dead:bool=False

    def die(self):
        if not self.dead:
            print(f'{self} hits the ground... DEAD')
            self.name=self.name + ' - (DEAD)'
            #maybe some loot function and/or creating a corpse object/container
            self.dead=True

    def equip(self, item=None):
        if isinstance(item, Armor|Weapon):
            print(f'{self.name} equips {item}.')
            if isinstance(item, Armor): self.armor=item
            elif isinstance(item, Weapon): self.weapon=item

        elif item==None:
            print(f'What would you like to equip {self} with?')
            
        else:
            print(f'{item} is not equipable')
            raise TypeError

    def __str__(self): return self.name
    
    def fight(self, other): 
       from combat import fight
       fight(self, other)


class Party(list):
# TODO: party grouping of mobiles
    def __init__(self, *mobile):
        super().__init__()
     
        if   isinstance(*mobile, Party):  self.join(mobile)
        elif isinstance(*mobile, Mobile): self.append(mobile)
    
    def __add__(self, other:Mobile):
        if isinstance(other, Mobile|Party): self.append(other)  
    
    def join(self, mobile):
        if   isinstance(mobile, Party):  self + mobile
        elif isinstance(mobile, Mobile): self + mobile
        return self

class Monster(Mobile):
    '''a simple monster constructor...'''
    def __init__(self, name:str='monster', hit_points:int=2, attack:int=1, defense:int=0):
        super().__init__(name, hit_points, attack, defense)