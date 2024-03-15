#!/usr/bin/env python3
import argparse
import threading
import time

import server
import actions

def splash_screen():
    print(r"""
     _  Eventually, there may be a                                
  __| |_   _ _ __   __ _  ___  ___  _ __  
 / _` | | | | '_ \ / _` |/ _ \/ _ \| '_ \ 
| (_| | |_| | | | | (_| |  __/ (_) | | | |
 \__,_|\__,_|_| |_|\__, |\___|\___/|_| |_|
                   |___/ (c)2024 Petrofang                  
""")
    

"""
TODO:
    * add open/close to container objects 
    * add lock/unlock to container objects
    * figure out how keys work
    
"""


parser = argparse.ArgumentParser(
    description=('Dungeon game (c) Petrofang 2024 - ', 
                 'https://github.com/petrofang/dungeon/'))
parser.add_argument(
    '--hacker_mode', action='store_true', 
    help='Import all modules and drop into Python shell (experts only)') 
args = parser.parse_args()

def process_game_updates():
    while True:
        time.sleep(6)
        actions.update_game()

def main():
    """The main game loop."""
    server.start_game_server()
#    server.enable_upnp_port_mapping()
    game_update_thread = threading.Thread(target = process_game_updates)
    game_update_thread.start()
    server.wait_for_connections()



def hacker_mode():
    """Import all modules and drop into Python shell (experts only)"""
    import code
    
    import actions, combat, commands, dice, dungeon_data
    import mobiles, objects, players, rooms, server
    code.interact(local=locals())

if __name__ == '__main__':
    splash_screen()
    if args.hacker_mode:
        hacker_mode()
    else:
        main()
