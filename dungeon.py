
from mobiles import global_mobiles, Mobile
from objects import Armor, Weapon, global_objects
from rooms import global_rooms
import players

DEBUG=True
INFO=False
PROMPT='\n > '
def debug(message): print(f'{__name__} DEBUG: {message}') if DEBUG else None
def info(message): print(f'INFO: {message}') if INFO else None
debug(f'{DEBUG}')
info(f'{INFO}')

def main():
    from commands import CommandList
    while True:
        user_input = input(PROMPT).lower()
        command, *args = user_input.split()
        command = getattr(CommandList, command, None)
        if command: 
            command(*args) if args else command()
        else: print(f'unknown command "{user_input}"')

if __name__=='__main__': 
    # prepare rooms
    from rooms import Room
    workshop=Room("Antron's Workshop", "A cottage contains a small but messy workshop of various projects in varying states of incompletion.")
    outside=Room("Potter's Field", 'The "Potter\'s field" is a place where potters have dug for clay, and thus a place conveniently full of trenches and holes for the burial of strangers.')
    workshop.exits['south']     = outside
    outside.exits['north']      = workshop

    # load or generate a character:
    user_input=input('(L)oad a character or (N)ew?' + PROMPT)
    if user_input.upper() == 'L': me = players.load()
    elif user_input.upper() == 'N': me = players.new()
    else: raise UserWarning('Listen: if you cannot follow basic prompts, this game is not for you.')
    if not me.room: me.room=workshop

    # prepare mobiles
    Mobile('goblin', room=workshop)
    Mobile('ugly goblin', room=workshop)
    Mobile('giant rat', room=workshop)
    Mobile('sickly kobold',5)
    Mobile('skeleton', 20, 5)
    Mobile('red goblin',23,4,1,room=workshop)
    Mobile('gelatinous cube',40,5,5)
    Mobile('vampire', 40, 10, 4)
    Mobile('mimic',50,10,0)
    Mobile('wraith',60,8,0, room=outside)
    Mobile('dragonkin', 80,10,10) 
    Mobile('dragon', 200, 20, 5)

    # prepare objects
    from objects import Weapon, Armor
    sword=Weapon('a rusty old sword')
    armor=Armor('some rusty old armor')
    workshop.objects[sword.id] = sword
    workshop.objects[armor.id] = armor
    workshop.look()
    outside.look()

    # anything else before entering main game loop
    
    main()