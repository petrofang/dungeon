#!/usr/bin/env python3

DEBUG = False
PROMPT=' >> '

def splash_screen():
    print(r"""
     _  Eventually, there may be a                                
  __| |_   _ _ __   __ _  ___  ___  _ __  
 / _` | | | | '_ \ / _` |/ _ \/ _ \| '_ \ 
| (_| | |_| | | | | (_| |  __/ (_) | | | |
 \__,_|\__,_|_| |_|\__, |\___|\___/|_| |_|
                   |___/ (c)2024 Petrofang                  
""")
    
import time, threading, argparse
import commands, actions, players

parser = argparse.ArgumentParser(description='Dungeon game (c) Petrofang 2024 - https://github.com/petrofang/dungeon/')
parser.add_argument( '-d', '--debug', action='store_true', help='Run in debug mode')
parser.add_argument( '--hacker_mode', action='store_true', help='Import all modules and drop into Python shell (experts only)') 
args = parser.parse_args()

def debug(message): print(f'{__name__} *** DEBUG *** {message}') if DEBUG else None
debug(f'{DEBUG}')

def process_game_updates():
    while True:
        time.sleep(6)
        actions.update_game()

def process_user_inputs(user=None):
    print(f'Hint: type HELP for a list of commands')
    while True: 
        user_input = input(PROMPT)
        commands.parse(user, user_input)

def init():
    # load or generate a character:
    me = None
    while not me:
        user_input=input('(L)oad a character or (N)ew?' + PROMPT)
        if user_input[0].upper() == 'N': me = players.new()
        elif user_input[0].upper() == 'L': me = players.load()
        else: print("...")  
    return me
    # perform other initialization tasks

def main(me="test"):
    me.room.look(me)
    game_update_thread = threading.Thread(target=process_game_updates)
    user_input_thread = threading.Thread(target=process_user_inputs, args=(me,))
    
    user_input_thread.start()
    game_update_thread.start()
    user_input_thread.join()
    game_update_thread.join()

def HACKER_MODE():
    import code
    import actions, combat, commands, dice, dungeon_data, mobiles, objects, players, rooms
    code.interact(local=locals())

def DEBUG_ROUTINE():
    test=players.load("Antron")
    commands.parse(test, "look sword")
    commands.parse(test, "look Beholder")

if __name__ == '__main__':
    splash_screen()
    if args.debug:
        DEBUG = True
        DEBUG_ROUTINE()
    if args.hacker_mode:
        DEBUG = True
        HACKER_MODE()
    else:
        main(init())
