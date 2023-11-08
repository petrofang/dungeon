from random import random
from time import sleep
from objects import *
from mobiles import *
from combat import *

DEBUG=True
def debug(message): print(f'DEBUG:{message}') if DEBUG else None
debug(f'{DEBUG} @ {__name__}')

def main():
    player=generate_player()

    monster_horde=[]
    monster_horde.append(Monster('goblin'))
    monster_horde.append(Monster('giant rat'))
    monster_horde.append(Monster('skeleton', 20, 5))
    monster_horde.append(Monster('vampire', 40, 10, 4))
    monster_horde.append(Monster('dragon', 200, 20, 5))

    print([str(monster) for monster in monster_horde])
    input('are you ready to fight the monster hoard? > ')
    print('rhetorical question... we begin now:')
    sleep(1)


    for monster in monster_horde:
        if not player.dead:
            print(f'{player} will now fight {monster}... to the death.')
            sleep(3)
            player.fight(monster)
    input()


if __name__=='__main__': main()