#objects.py

DEBUG=False
INFO=False
def debug(message): print(f'{__name__} DEBUG: {message}') if DEBUG else None
def info(message):  print(f'{__name__} INFO: {message}')  if INFO  else None
debug(f'{DEBUG}')
info(f'{INFO}')

global_objects = {}

class Object: 
    def __init__(self, name:str='thing', **kwargs):
        from mobiles import Mobile
        from rooms import Room
        self.id = id(self)
        self.name = name
        info(f'{self.name} is created (ID:{self.id})')
        if not isinstance(self, (Mobile, Room)): global_objects[self.id]=self
        for key, val in kwargs: self[key]=val

    def __del__(self):
        info(f'{self} vanishes into thin air.')

    def __str__(self): return self.name

class Weapon(Object):
    def __init__(self, name: str = 'weapon', weapon_rating:int=1):
        super().__init__(name)
        self.rating = weapon_rating

class Armor(Object):
    def __init__(self, name='armor', armor_rating:int=1):
        super().__init__(name)
        self.rating = armor_rating
    
