#players.py
DEBUG=False
INFO=False
def debug(message): print(f'{__name__} DEBUG: {message}') if DEBUG else None
def info(message):  print(f'{__name__} INFO: {message}')  if INFO  else None
debug(f'{DEBUG}')
info(f'{INFO}')

import pickle
from time import sleep
from mobiles_OLD import Mobile

class PlayerCharacter(Mobile):
    def __init__(self, name:str='adventurer', hit_points:int=100, attack=10, defense=5, **kwargs) -> None:
        super().__init__(name, hit_points, attack, defense, **kwargs)
        self.id=self.name

    def save(self):
        ''' save a player-character to file '''
        # TODO: use os.path to get the right working directory.
        # FIXME: create players directory if not found
        # FIXME: don't save self.room -- but do save the room ID
        with open(f"./players/{self.name}.player", "wb") as f: 
            pickle.dump(self, f)
            print(f'{self} saved to file.')
    
    def level_up(self):
        self.attack+=1
        self.defense+=1
        print(f'{self} has leveled up.')
        print(f'attack:{self.attack}')
        print(f'defense:{self.defense}')
        
    
def load(player_name:str=None) -> PlayerCharacter:
    ''' load a player-character from file. '''
    if player_name == None: 
        player_name=input('What player name would you like to load?\n > ')

    try:
        with open(f"./players/{player_name}.player", "rb") as f: 
            player = pickle.load(f)
            print(f'{player} has been loaded from file.')

    except FileNotFoundError:
        print(f'No playerfile located for {player_name}')
        player=None

    except pickle.UnpicklingError:
        print(f'Error loading {player_name}\'s file. ')
        player=None
    
    return player


def new(name:str=None) -> PlayerCharacter:
    ''' generate a new player-character object '''
    print(" --- New character generation ---")
    if name==None: 
        _name='adventurer'
        name=input(f'What is you name, {_name}? > ')
    sleep(0.5)
    if name == '': 
        name=_name
        return PlayerCharacter(name)
    try:
        # check if the player name already exists by looking for their file
        f = open(f'{name}.player', 'rb')
    except FileNotFoundError:
        print(f'Very well, {name}...')
        player=PlayerCharacter(name)
        return player
    else: 
        f.close()
        print('That name is already taken.')
        # if so, just return a default adventurer
        return PlayerCharacter()