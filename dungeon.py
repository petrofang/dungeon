from random import random
from time import asctime, sleep
from objects import *
from mobiles import *
from combat import *
import players
import pickle


DEBUG=True
def debug(message): print(f'{__name__} DEBUG:{message}') if DEBUG else None
debug(f'{DEBUG}')

    

def main():
    player=players.load('rogue')
    if not player:player=players.new()

    monster_horde=[]
    monster_horde.append(Monster('goblin'))
    monster_horde.append(Monster('stirge'))
  #  monster_horde.append(Monster('giant rat'))
   # monster_horde.append(Monster('skeleton', 20, 5))
  #  monster_horde.append(Monster('vampire', 40, 10, 4))
   # monster_horde.append(Monster('dragon', 200, 20, 5))

    print([str(monster) for monster in monster_horde])
    input('are you ready to fight the monster hoard? > ')
    print('rhetorical question... we begin now:')
    sleep(1)

    if player:
        for monster in monster_horde:
            print(f'{player} will now fight {monster}... to the death.')
            sleep(3)
            player.fight(monster)
        players.save(player)

if __name__=='__main__': main()