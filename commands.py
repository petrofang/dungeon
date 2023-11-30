
DEBUG=True
INFO=False
PROMPT='  > '
def debug(message): print(f'{__name__} DEBUG: {message}') if DEBUG else None
def info(message): print(f'INFO: {message}') if INFO else None
debug(f'{DEBUG}')
info(f'{INFO}')

class CommandList():
    def __no_dunders(command:str): 
        ''' filter to show only public commands'''
        return not command.startswith('_')

    def help(command=None):
        '''  help          - get a list of commands.
  help(command) - show help for a command.'''
        list_of_commands=filter(CommandList.__no_dunders, vars(CommandList))
        if command == None:
            print(CommandList.help.__doc__)
            print('\n --- Command List ---')
            for each in list_of_commands:
                print(f'    {each}')
        elif command in list_of_commands:
            command = getattr(CommandList, command)
            print(command.__doc__)

    def quit():
        '''  quit - quit the game (without saving) '''
        quit()

def main():
    while True:
        user_input = input(PROMPT).lower()
        command, *args = user_input.split()
        command = getattr(CommandList, command, None)
        if command: 
            command(*args) if args else command()
        else: print(f'unknown command "{user_input}"')


if __name__ == '__main__': main()