#mobiles.py

from objects import Object,Armor,Weapon
from rooms import Room

DEBUG=False
INFO=False
def debug(message): print(f'{__name__} DEBUG: {message}') if DEBUG else None
def info(message):  print(f'{__name__} INFO: {message}')  if INFO  else None
debug(f'{DEBUG}')
info(f'{INFO}')

global_mobiles={}

class Mobile(Object): 
    ''' a mobile (living, moving entity)
    
    base class for many other types of creature, including players.
    '''
    def __init__(self, name:str='NPC', hit_points:int=1, attack:int=0, defense:int=0, room:Room=None):
        super().__init__(name)
        self.hit_points:int=hit_points
        self.name:str = name
        self.attack:int = attack
        self.defense:int = defense
        self.armor:Armor = None
        self.weapon:Weapon = None
        self.dead:bool = False      # TODO: get rid of this
        self.inventory:dict = {}    # would this be better as a list?
        self.room:Room = room 
        if isinstance(self.room, Room): self.room.mobiles[self.id]=self

    def die(self):
        from players import PlayerCharacter
        from objects import Corpse
        ''' how to die (a psuedo-deconstructor)'''
        print(f'{self} hits the ground... DEAD')
        if type(self) is not PlayerCharacter:
            if self.weapon:
                self.room.objects[self.weapon.id]=self.weapon
            if self.armor:
                self.room.objects[self.armor.id]=self.armor
            if self.inventory:
                for item in self.inventory:
                    self.room.objects[item.id]=self.inventory.pop(item.id)
            Corpse(self.name, self.room)
            self.room.mobiles.pop(self.id)
        else:
            # PlayerCharacter death:
            quit()


    def get(self, item:Object):
        if item in self.room.objects.values():
            self.inventory[item.id]=self.room.objects.pop(item.id)
            print(f'{self} picks up {item}.')
    
    def drop(self, item:Object):
        if item not in self.inventory.values():
            raise UnboundLocalError(f"{self} doesn't have {item} in inventory.")
        else:
            self.room.objects[item.id]=self.inventory.pop(item.id)
            print(f'{self} drops {item} on the ground.')

    def equip(self, item:Object=None):
        if isinstance(item, (Armor, Weapon)):
            if isinstance(item, Armor): self.armor=item
            elif isinstance(item, Weapon): self.weapon=item
            print(f'{self.name} equips {item}.')

    def unequip(self, item:Object=None):
        if self.armor is item:
            self.inventory[item.id]=item
            self.armor=None
        if self.weapon is item:
            self.inventory[item.id]=item
            self.weapon=None
        print(f'{self} unequips {item}.')
    
    def fight(self, other): 
       from combat import fight
       fight(self, other)

    # TODO: Move individual attacks back to mobile class

def main():
    here   = Room()
    goblin = Mobile('goblin', room=here)
    sword  = Weapon('rusty sword')
    armor  = Armor( 'light armor')
    here.objects[sword.id]=sword
    here.objects[armor.id]=armor
    goblin.get(sword)
    goblin.get(armor)
    goblin.equip(sword)
    goblin.equip(armor)
    goblin.unequip(sword)
    goblin.unequip(armor)
    goblin.drop(sword)
    goblin.drop(armor)
    here.look()

if __name__=="__main__": main()