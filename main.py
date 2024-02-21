def splash_screen():
    print(r"""
     _  Eventually, there may be a                                
  __| |_   _ _ __   __ _  ___  ___  _ __  
 / _` | | | | '_ \ / _` |/ _ \/ _ \| '_ \ 
| (_| | |_| | | | | (_| |  __/ (_) | | | |
 \__,_|\__,_|_| |_|\__, |\___|\___/|_| |_|
                   |___/ (c)2024 Petrofang                  
""")
PROMPT=' >> '

DEBUG=True
def debug(message): print(f' *** DEBUG *** {message}') if DEBUG else None
debug(f'{DEBUG}')

def DEBUG_ROUTINE():
    main(players.load("test"))

import players, rooms

def main(me=players.PlayerCharacter):
    if not me: raise UserWarning("who?")
    from commands import CommandList
    rooms.look(me.room_id)
    print(f'Hint: type HELP for a list of commands')
    while True:
        user_input = input(PROMPT).lower()
        if user_input:
            command, *args = user_input.split()
            command = getattr(CommandList, command, None)
            if command: 
                command(*args, me=me) if args else command(me=me)
            else: print(f'Unknown command "{user_input}".')
        else: print('Huh?')

def init(): # initilization tasks:
    splash_screen()
    me = None
    # load or generate a character:
    while not me:
        user_input=input('(L)oad a character or (N)ew?' + PROMPT)
        if user_input.upper() == 'N': me = players.new()
        elif user_input.upper() == 'L': me = players.load()
        else: print("...")
    main(me)

if __name__=='__main__': 
    if DEBUG:
        DEBUG_ROUTINE()
    else:
        init()
