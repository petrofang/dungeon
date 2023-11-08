#mobiles.py

from random import random
from objects import Object

DEBUG=True
def debug(message): print(f'{__name__} DEBUG:{message}') if DEBUG else None
debug(f'{DEBUG}')


class Mobile(Object): 
    def __init__(self, name:str='', hit_points=0, attack=0, defense=0):
        super().__init__(self, name)
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
        import combat
        combat.fight(self, other)

class Monster(Mobile):
    '''a simple monster constructor...'''
    def __init__(self, name:str='monster', hit_points:int=2, attack:int=1, defense:int=0):
        Mobile.__init__(self, name, hit_points, attack, defense)


                
    
