#dungeon.py

from random import random
from time import sleep

class mobile: pass
    # TODO: make this a master class the monster and PC can inherit from

class Monster:
    def __init__(self, name:str='monster', hp:int=2, attack:int=1, defense:int=0):
        self.hit_points = hp
        self.name = name
        self.attack = attack
        self.defense = defense
        self.dead=False

    def __str__(self): return self.name
    
    def fight(self, other): fight(self, other)


class PlayerCharacter:
    def __init__(self, name:str='adventurer', hp:int=100, dmg=10, defense=1) -> None:
        self.hit_points = hp
        self.name = name
        self.attack = dmg
        self.defense = defense
        self.dead=False

    def __str__(self): return self.name

    def fight(self, other): fight(self, other)

def d20_roll(n:int=1): return int(1+(random()*20//1))

def fight(me, them):
  if not them.dead:  
    me.roll=d20_roll()
    them.roll=d20_roll()
    print(f'{me} makes an attack at {them}!')
    sleep(3)
    print(f'{me}\'s attack: {me.attack}')
    print(f'{them}\'s defense: {them.defense}')
    sleep(3)
    print(f'{me}\'s d20: {me.roll}.')
    print(f'{them}\'s d20: {them.roll}')
    sleep(3)
    damage = me.roll + me.attack - them.roll - them.defense
    if damage > 0:
        print("It's a hit!")
        sleep(2)
        print(f'damage = ({me.roll} + {me.attack}) - ({them.roll} + {them.defense})')

        print(f'{damage} damage done to {them}!')
        them.hit_points-=damage
        sleep(2)
        print(f'{them} HP remaining: {max(0, them.hit_points)}')
        sleep(2)
    else:
        print("Swing and a miss!")
    sleep(3)

    if them.hit_points < 1:
        # oh them dead
        them.dead=True
        sleep(3)
        print(f'the lifeless body of {them} hits the ground... dead.')
        sleep(3)
        print(f'{me} is victorious.')
        me.defense+=1
        me.attack+=1
        print(f'{me} attack raised to {me.attack}.')
        print(f'{me} defense raised to {me.defense}.')
    else:
        print(f'{them} fights back!')
        print('---------------------')
        them.fight(me)
  else: print(f'{them} is aleady dead.')

def main():
    player=PlayerCharacter()
    player.name=input(f'What is you name, {player.name}? > ')
    

    monster_horde=[]
    monster_horde.append(Monster('goblin'))
    monster_horde.append(Monster('R.O.U.S.'))
    monster_horde.append(Monster('skeleton', 20, 5))
    monster_horde.append(Monster('Vampire', 40, 10, 4))
    monster_horde.append(Monster('dragon', 200, 20, 5))

    print([str(monster) for monster in monster_horde])
    input('are you ready to fight the monster hoard?')
    print('rhetorical question... we begin:')


    for monster in monster_horde:
        if not player.dead:
            print(f'{player} will now fight {monster}... to the death.')
            sleep(5)
            monster.fight(player)
    input()

if __name__=='__main__': main()