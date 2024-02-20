# rooms.py
from objects_OLD import Object

DEBUG=False
INFO=False
def debug(message): print(f'{__name__} DEBUG:{message}') if DEBUG else None
def info(message): print(f'INFO:{message}') if INFO else None
info(f'{INFO}')
debug(f'{DEBUG}')

global_rooms={}

class Room(Object):
    def __init__(self, name:str='Room', description:str='An empty area.', **exits):
        super().__init__(name)
        self.description = description
        self.objects = {}  # [obj.id]=obj
        self.mobiles = {}  # [mob.id]=mob
        self.exits={} # [direction]=room.id 
        for direction,room_id in exits:
            self.exits[direction]=room_id
        global_rooms[self.id]=self

    def look(self):
        print(f'[{self.name}]', end="")
        if INFO: print('ID: {self.id})')
        else: print()
        print(f'    {self.description}', end=' ')
        if self.objects:
            object_list=list(self.objects.values())
            print(f'There is:', end="")
            for index, item in enumerate(object_list,1):
                print(f" {item.name}", end="")
                if index < len(object_list):
                    print(',', end='')
                else:
                    print('.')
        if self.mobiles:
            print('Also here:', end="")
            mobile_list=list(self.mobiles.values())
            for index, mobile in enumerate(mobile_list,1):
                print(f" {mobile.name}", end="")
                if index < len(mobile_list):
                    print(',', end='')
                else:
                    print('.')
        else: print()
        print('Exits: ', end='')
        if not self.exits: print('None')
        else:
            for direction, room in self.exits.items():
                print(f'{direction}: {room.name}')
        print()

def main():
    from objects_OLD import Weapon, Armor
    workshop=Room("Antron's Workshop", "A cottage contains a small but messy workshop of various projects in varying states of incompletion.")
    outside=Room("Potter's Field", 'The "Potter\'s field" is a place where potters dug for clay, and thus a place conveniently full of trenches and holes for the burial of strangers.')
    workshop.exits['south']     = outside
    outside.exits['north']      = workshop
    sword=Weapon('a rusty old sword')
    armor=Armor('some rusty old armor')
    workshop.objects[sword.id] = sword
    workshop.objects[armor.id] = armor
    workshop.look()
    outside.look()

if __name__=="__main__": main()