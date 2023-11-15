DEBUG=True
def debug(message): print(f'{__name__} DEBUG:{message}') if DEBUG else None
debug(f'{DEBUG}')

import pickle
from time import sleep
from mobiles import Mobile

class PlayerCharacter(Mobile):
    def __init__(self, name:str='adventurer', hit_points:int=100, attack=10, defense=5) -> None:
        super().__init__(name, hit_points, attack, defense)
    
    def save(self):
        ''' save a player-character to file '''
        with open(f"./players/{self.name}.player", "wb") as f: 
            pickle.dump(self, f)
            print(f'{self} saved to file, probably...')
    
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


def new(name=None) -> PlayerCharacter:
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
        f.close()
        print('That name is already taken.')
        # if so, just return a default adventurer
        return PlayerCharacter()
    except FileNotFoundError:
        print(f'Very well, {name}...')
        player=PlayerCharacter(name)
        return player
    else: 
        f.close()
