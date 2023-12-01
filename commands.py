from objects import Armor, Weapon
from players import PlayerCharacter

DEBUG=False
INFO=False
def debug(message): print(f'{__name__} DEBUG: {message}') if DEBUG else None
def info(message): print(f'INFO: {message}') if INFO else None
debug(f'{DEBUG}')
info(f'{INFO}')

class CommandList():
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

    def _whoami(*args, me:PlayerCharacter=None, **kwargs):
        ''' WhoAmI - Print the name of the player who called the function.'''
        print(f'You are {str(me).capitalize()}.') if me else UserWarning('Who even are you?')

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
        for each_item in me.inventory.values():
            print(each_item)

    def equip(*args, me:PlayerCharacter=None, **kwargs):
        ''' Equip       - Show equipped items.
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
        if not args: 
            print('Unequip what now?')
            return
        item=None
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

    # abbreviations and shortcuts:
    inv=inventory
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