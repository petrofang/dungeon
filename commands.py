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
        '''  Help           - get a list of commands.
  Help <command> - show help for a command.'''
        list_of_commands=filter(CommandList.__no_dunders, vars(CommandList))
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
        '''  Quit - quit the game (without saving). '''
        quit()

    def whoami(*args, me:PlayerCharacter=None):
        '''  WhoAmI - Print the name of the player who called the function.'''
        print(f'You are {me}.') if me else UserWarning('Who even are you?')

    def look(*args, me:PlayerCharacter=None):
        '''  Look - take a look at the place you are in. '''
        if not me.room:
            print('You are nowhere. You do not have a location yet.')
        else:
            me.room.look()
    l=look

def main():
    from dungeon import PROMPT
    from players import PlayerCharacter
    me=PlayerCharacter
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