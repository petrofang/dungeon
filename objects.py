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

    def __str__(self): return self.name

class Weapon(Object):
    def __init__(self, name: str = 'weapon'):
        super().__init__(name)

class Armor(Object):
    armor_bonus=1
    def __init__(self, name='armor', armor_rating=1):
        super().__init__(self, name)
        self.armor_rating=armor_rating
    
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
