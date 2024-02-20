#commands.py
from objects_OLD import Armor, Weapon
from players import PlayerCharacter

DEBUG=False
INFO=False
def debug(message): print(f'{__name__} DEBUG: {message}') if DEBUG else None
def info(message): print(f'INFO: {message}') if INFO else None
debug(f'{DEBUG}')
info(f'{INFO}')

class CommandList():
    ''' This is the master list of all player commands. 

    Usage: 

command, *args = input().split()
command = getattr(CommandList, command, None)
if command: command(*args, me=player) if args else command(me=player)
'''
    def __no_dunders(command:str): 
        ''' A filter to show only public commands on the help list.'''
        return not command.startswith('_')

    def help(command=None, *args, **kwargs):
        ''' Help           - get a list of commands.
 Help <command> - show help for a command.'''
        list_of_commands = sorted(filter(CommandList.__no_dunders, vars(CommandList)))
        if command == None:
            print(CommandList.help.__doc__)
            print('\n --- Command List ---')
            for each in list_of_commands:
                print(f'    {each}')
        elif command in list_of_commands:
            command = getattr(CommandList, command)
            print(command.__doc__)        
        else: print(f'Unknown command "{command}".')

    def quit(*args, **kwargs):
        # TODO: not so unceremoniously
        ''' Quit - quit the game (without saving). '''
        quit()

    def look(*args, me:PlayerCharacter=None, **kwargs):
        ''' Look - take a look at the place you are in. '''
        if not me.room:
            print('You are nowhere. You do not have a location yet.')
        else:
            me.room.look()

    def get(*args, me:PlayerCharacter=None, **kwargs):
        ''' Get <item> - Get an item from the room. '''
        # TODO: "get all"
        room=me.room.objects
        item_name=args[-1] if args else None
        item=None
        if room and args:
            for each_item in room.values():
                if item_name in each_item.name:
                    item=each_item
                    break
            if item is not None:
                me.inventory[item.id]=me.room.objects[item.id]
                me.room.objects.pop(item.id)
                print(f'{str(me).capitalize()} picks up {item}.')
            else: 
                print(f'There is no {args[-1]} here.')
        elif not room: print('There is nothing here to get.')
        elif not args: print('Get what now?') 

    def drop(*args, me:PlayerCharacter=None, **kwargs):
        ''' Drop <item> - Drop an item on the ground. '''
        # TODO: "drop all"
        if not args: 
            print('Drop what now?')
            return
        item=None
        for each_item in me.inventory.values():
            if args[-1] in each_item.name:
                item = each_item
        if item is None and args[-1] in me.weapon.name:
            item=me.weapon
            me.room.objects[item.id]=item
            me.weapon=None
            print(f'{str(me).capitalize()} drops {item} on the ground.')
            return
        if item is not None:
            me.room.objects[item.id]=me.inventory.pop(item.id)
            print(f'{str(me).capitalize()} drops {item} on the ground.')
        else:     
            print(f"{str(me).capitalize()} doesn't have {args[-1]} in inventory.")

    def inventory(*args, me:PlayerCharacter=None, **kwargs):
        ''' Inventory - Check inventory. '''
        title=(f'  {str(me).capitalize()}\'s Inventory  ')
        print(title)
        print('-'*len(title))
        if me.inventory: 
            for each_item in me.inventory.values():
                print(each_item)
        else: print('None')

    def wear(*args, me:PlayerCharacter=None, **kwargs):
        ''' Wear <item> - Wear an item. '''
        item=None
        for each_item in me.inventory.values():
            if args[-1] in each_item.name:
                item = each_item
        if isinstance(item, Armor): 
            CommandList.equip(*args, me=me)
        else:
            print(f'You cannot wear that.')

    def remove(*args, me:PlayerCharacter=None, **kwargs):
        ''' Remove <item> - Remove a worn item. '''
        if args[-1] in me.armor.name:
            CommandList.unequip(*args, me=me)
        else:
            print(f'You are not wearing that.')

    def wield(*args, me:PlayerCharacter=None, **kwargs):
        ''' Wield <weapon> - Equip a weapon. '''
        item=None
        for each_item in me.inventory.values():
            if args[-1] in each_item.name:
                item = each_item
        if isinstance(item, Weapon): 
            CommandList.equip(*args, me=me)
        else:
            print(f'You cannot wield that.')
                  
    def equip(*args, me:PlayerCharacter=None, **kwargs):
        ''' Equip        - Show equipped items.
 Equip <item> - Equip an item. '''
        if not args: 
            title=(f'  {str(me).capitalize()}\'s Equipment  ')
            print(title)
            print('-'*len(title))
            print(f'Armor: {me.armor}')
            print(f'Weapon: {me.weapon}')
            return
        item=None
        for each_item in me.inventory.values():
            if args[-1] in each_item.name:
                item = each_item
        if item is not None:
            if isinstance(item, Armor): 
                if me.armor:
                    print(f'{me.armor.name.capitalize()} is already equipped.')
                else:
                    me.armor=me.inventory.pop(item.id)
                    print(f'{str(me).capitalize()} wears {item}.')
            elif isinstance(item, Weapon): 
                if me.weapon:
                    print(f'{me.weapon.name.capitalize()} is already equipped.')
                else:
                    me.weapon=me.inventory.pop(item.id)
                    print(f'{str(me).capitalize()} wields {item}.')
            else:
                    print(f'{item.name.capitalize()} is not something you can equip.')
        else:     
            print(f"{str(me).capitalize()} doesn't have {args[-1]} in inventory.")

    def unequip(*args, me:PlayerCharacter=None, **kwargs):
        ''' Unequip <item> - Unequip an item or weapon. '''
        if not args: 
            print('Unequip what now?')
            return
        if me.armor:
          if args[-1] in me.armor.name:
            me.inventory[me.armor.id]=me.armor
            print(f'{str(me).capitalize()} removes {me.armor}.')
            me.armor=None
            return
        if me.weapon:
          if args[-1] in me.weapon.name:
            me.inventory[me.weapon.id]=me.weapon
            print(f'{str(me).capitalize()} unequips {me.weapon}.')
            me.weapon=None
            return
        else:     
            print(f"{str(me).capitalize()} doesn't have {args[-1]} equipped.")

    def fight(*args, me=None, **kwargs):
        ''' Fight <target> - Initiate combat.'''
        room=me.room.mobiles
        mob_name=args[-1] if args else None
        mob=None
        if room and args:
            for each in room.values():
                if mob_name in each.name and each.dead==False:
                    mob=each
                    break
            if mob is not None:
                from combat import fight
                print(f'{str(me).capitalize()} lunges at {mob}.')
                fight(me, mob)
            else: 
                print(f'There is no {args[-1]} here.')
        elif not room: print('There is nobody here to fight.')
        elif not args: print('Fight who now?') 

    def save(*args, me:PlayerCharacter=None, **kwargs):
        # TODO: differenciate between saving the character and saving the game
        #       . . . or not? single-player, who cares?
        me.save()

    def go(*args, me:PlayerCharacter=None, **kwargs): #N,NE,E,SE,S,SW,W,NW,Up,Down,Out
        ''' Go <direction> - move into the next room in <direction>
     for cardinal directions you can just type the direction, eg:
     <north|east|south|west|[etc.]> or <N|NE|E|SE|S|SW|W|NW>'''
        dir=args[0]
        if dir=='n':dir='north'
        if dir=='ne':dir='northeast'
        if dir=='e':dir='east'
        if dir=='se': dir='southeast'
        if dir=='s':dir='south'
        if dir=='sw':dir='southwest'
        if dir=='w':dir='west'
        if dir=='nw':dir='northwest'
        if dir in me.room.exits:
            # move player to the room in that direction
            print(f'{me.name.capitalize()} heads {dir}.')
            me.room=me.room.exits[dir]
            me.room.look()

    def north(*args, me:PlayerCharacter=None, **kwargs):
        ''' alias for GO NORTH.'''
        CommandList.go('north', me=me)
    def northeast(*args, me:PlayerCharacter=None, **kwargs):
        ''' alias for GO NORTHEAST.'''
        CommandList.go('northeast', me=me)
    def east(*args, me:PlayerCharacter=None, **kwargs):
        ''' alias for GO EAST.'''
        CommandList.go('east', me=me)
    def southeast(*args, me:PlayerCharacter=None, **kwargs):
        ''' alias for GO SOUTHEAST.'''
        CommandList.go('southeast', me=me)
    def south(*args, me:PlayerCharacter=None, **kwargs):
        ''' alias for GO SOUTH.'''
        CommandList.go('south', me=me)
    def southwest(*args, me:PlayerCharacter=None, **kwargs):
        ''' alias for GO SOUTHWEST.'''
        CommandList.go('southwest', me=me)
    def west(*args, me:PlayerCharacter=None, **kwargs):
        ''' alias for GO WEST.'''
        CommandList.go('west', me=me)
    def northwest(*args, me:PlayerCharacter=None, **kwargs):
        ''' alias for GO NORTHWEST'''
        CommandList.go('northwest', me=me)
    
    
        
    # abbreviations and shortcuts:
    inv=inventory
    n=north
    ne=northeast
    e=east
    se=southeast
    s=south
    sw=southwest
    w=west
    nw=northwest
    l=look
    q=quit

def main():
    from dungeon import PROMPT
    from players import PlayerCharacter
    me=PlayerCharacter()
    CommandList.help()
    while True:
        user_input = input(PROMPT).lower()
        if user_input:
            command, *args = user_input.split()
            command = getattr(CommandList, command, None)
            if command: 
                command(*args, me=me) if args else command(me=me)
            else: print(f'Unknown command "{user_input}".')
        else: print('Huh?')


if __name__ == '__main__': main()