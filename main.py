#!/usr/bin/env python3
def splash_screen():
    print(r"""
     _  Eventually, there may be a                                
  __| |_   _ _ __   __ _  ___  ___  _ __  
 / _` | | | | '_ \ / _` |/ _ \/ _ \| '_ \ 
| (_| | |_| | | | | (_| |  __/ (_) | | | |
 \__,_|\__,_|_| |_|\__, |\___|\___/|_| |_|
                   |___/ (c)2024 Petrofang                  
""")

DEBUG=True
PROMPT=' >> '

import players, rooms, commands

def debug(message): print(f'{__name__} *** DEBUG *** {message}') if DEBUG else None
debug(f'{DEBUG}')

def DEBUG_ROUTINE():
    me=players.load("test")
    main(me)
    
def main(me=players.PlayerCharacter):
    rooms.look(me)
    print(f'Hint: type HELP for a list of commands')
    while True:
        commands.parse(me, input(PROMPT))
 

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
