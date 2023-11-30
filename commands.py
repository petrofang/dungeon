from players import PlayerCharacter

DEBUG=True
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
        '''  Help           - get a list of commands.
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
        '''  Quit - quit the game (without saving). '''
        quit()

    def whoami(*args, me:PlayerCharacter=None, **kwargs):
        '''  WhoAmI - Print the name of the player who called the function.'''
        print(f'You are {me}.') if me else UserWarning('Who even are you?')

    def look(*args, me:PlayerCharacter=None, **kwargs):
        '''  Look - take a look at the place you are in. '''
        if not me.room:
            print('You are nowhere. You do not have a location yet.')
        else:
            me.room.look()

    def get(*args, me:PlayerCharacter=None, **kwargs):
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
        elif not room: print('There is nothing here to get.')
        elif not args: print('Get what now?')
        elif item == None: print(f'You do not find {args[-1]} here.')
        else: raise LookupError

    def drop(*args, me:PlayerCharacter=None, **kwargs):
        debug(args)
        if not args: 
            print('Drop what now?')
            return
        item=None
        debug(f'{me.inventory}')
        for each_item in me.inventory.values():
            debug(f'item: {each_item.name}')
            if args[-1] in each_item.name:
                item = each_item
        if item is not None:
            me.room.objects[item.id]=me.inventory.pop(item.id)
            print(f'{me} drops {item} on the ground.')
        else:     
            print(f"{str(me).capitalize()} doesn't have {args[-1]} in inventory.")
            

    # abbreviations and shortcuts:
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