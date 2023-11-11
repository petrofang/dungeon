from time import  sleep
from mobiles import Monster, Mobile
import players

DEBUG=True
def debug(message): print(f'{__name__} DEBUG:{message}') if DEBUG else None
debug(f'{DEBUG}')

def who(Type:type=players.Mobile)-> dict:
    ''' prints all active mobiles by name and object. '''
    try:  
        from gc import get_objects
        mobileDictionary={[mob.name for mob in get_objects() if isinstance(mob, Type)][i]:[mob for mob in get_objects() if isinstance(mob, Type)][i] for i in range(len([mob for mob in get_objects() if isinstance(mob, Type)]))}
        for i in mobileDictionary.keys(): print(f'{mobileDictionary[i].name:<20} :: {repr(mobileDictionary[i])}')
    except AttributeError:
        debug(f'{AttributeError}')
        objList=[obj for obj in get_objects() if isinstance(obj, Type)]
        print(objList)

def main():
    player=players.load()
    if not player:player=players.new()

    monster_horde=[]
    monster_horde.append(Monster('goblin'))
    monster_horde.append(Monster('ugly goblin'))
    monster_horde.append(Monster('giant rat'))
    monster_horde.append(Monster('skeleton', 20, 5))
  #  monster_horde.append(Monster('vampire', 40, 10, 4))
   # monster_horde.append(Monster('dragon', 200, 20, 5))

    print([str(monster) for monster in monster_horde])
    input('are you ready to fight the monster horde? > ')
    print('rhetorical question... we begin now:')
    sleep(1)

    player.fight(monster_horde)
    player.save()

if __name__=='__main__': main()