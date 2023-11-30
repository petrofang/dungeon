#mobiles.py

from objects import Object,Armor,Weapon

from rooms import Room

DEBUG=True   
def debug(message): print(f'{__name__} DEBUG:{message}') if DEBUG else None
debug(f'{DEBUG}')

global_mobiles={}

class Mobile(Object): 
    ''' a mobile (living, moving entity)
    
    base class for many other types of creature, including players.
    '''
    def __init__(self, name:str='', hit_points:int=1, attack:int=0, defense:int=0, room:Room=None):
        super().__init__(name)
        self.hit_points:int=hit_points
        self.name:str = name
        self.attack:int = attack
        self.defense:int = defense
        self.armor:Armor = None
        self.weapon:Weapon = None
        self.dead:bool = False
        self.inventory:dict = {}
        self.room:Room = room 
        if isinstance(self.room, Room): self.room.mobiles[self.id]=self
        # FIXME: change this when we add multiplayer:
        from players import PlayerCharacter
        if not isinstance(self, PlayerCharacter): global_mobiles[self.id] = self

    def die(self):
        ''' how to die (a psuedo-deconstructor)'''
        if not self.dead:
            print(f'{self} hits the ground... DEAD')
            self.name=self.name + ' - (DEAD)'
            if self.weapon: pass

            # TODO: maybe some loot function and/or creating a corpse object/container
            self.dead=True

    def get(self, item:Object=None):
        if not item: print('Get what now?')
        if isinstance(item, (Mobile, Room)): 
            print(f'{self} cannot carry {item}')
        else:    
            if item in self.room.objects.values():
                self.inventory[item.id]=self.room.objects.pop(item.id)
                print(f'{self} picks up {item}.')
    
    def drop(self, item:Object=None):
        if not item: print('Drop what now?')
        if item not in self.inventory.values():
            print(f"{self} doesn't have {item} in inventory.")
        else:
            self.room.objects[item.id]=self.inventory.pop(item.id)
            print(f'{self} drops {item} on the ground.')

    def equip(self, item:Object=None):
        if isinstance(item, (Armor, Weapon)):
            print(f'{self.name} equips {item}.')
            if isinstance(item, Armor): self.armor=item
            elif isinstance(item, Weapon): self.weapon=item
        elif item==None:
            print(f'What would you like to equip {self} with?')
        else:
            print(f'{str(item)} is not equipable.')

    def unequip(self, item:Object=None):
        if item is None:
            print('Unequip what?')
            return
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