#objects.py
from random import random
from time import time

DEBUG=True
def debug(message): print(f'{__name__} DEBUG:{message}') if DEBUG else None
debug(f'{DEBUG}')

class Object:
    def __init__(self, name:str='thing'):
        # set object ID to a hopefully-unique identifier
        self.id=abs(int((time()*10) % 10**10)-10**10)
        self.name=name

    def __del__(self):
        print(f'{self} vanishes into thin air.')

    def __str__(self): return self.name

class Weapon(Object):
    def __init__(self, name: str = 'weapon', weapon_rating:int=1):
        Object.__init__(name)
        self.rating=weapon_rating

class Armor(Object):
    armor_bonus=1
    def __init__(self, name='armor', armor_rating=1):
        Object.__init__(self, name)
        self.rating=rating
    
    def __add__(self, other):
        if type(other)==int: return self.armor_rating+other
        if type(other)==Object: return print(f'{self} and {other} cannot be combined')
        else: return None

    def equip(self): self.equipped=True
    
    def unequip(self): self.equipped=False
    
def d20_roll(n:int=1): return n*(int(1+(random()*20//1)))

def generate_armor():
    Armor.armor_bonus+=2
    armor_rating=Armor.armor_bonus
    return Armor(f'+{armor_rating} armor', armor_rating)
