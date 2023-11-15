# rooms.py
from objects import Object

DEBUG=True
def debug(message): print(f'{__name__} DEBUG:{message}') if DEBUG else None
debug(f'{DEBUG}')

class Room(Object):
    def __init__(self, name='room', description='This is a newly-instantiated room area.'):
        super().__init__(name)
        self.description = description
        self.objects = []  # the room's "inventory"
        self.inventory = self.objects # if we forget that rooms don't have inventory
        self.mobiles = []  # who is in the room
        self.exits={} # e.g. {north:<rooms.Object.Room object>,}

    def look(self):
        print(f'[{self.name}]')
        description=self.description
        if self.objects:
            obj_list='There is '
            for index, each in enumerate(self.objects, start=1):
                if index < len(self.objects):
                    obj_list += f'{each.name}, '
                elif index == len(self.objects):
                    obj_list += f'{each.name}.'
                else: raise ValueError # wait how did we get here?

        if self.mobiles:
            mob_list=f'Also here: '
            for index, each in enumerate(self.mobiles, start=1):
                if index < len(self.mobiles):
                    mob_list += f'{each.name}, '
                elif index == len(self.mobiles):
                    mob_list += f'{each.name}.'
                else: raise ValueError # wait how did we get here?
        print(f'{description} {obj_list}\n{mob_list}')