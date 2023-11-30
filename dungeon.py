def splash_screen():
    print(r"""
     _  Eventually, there may be a                                
  __| |_   _ _ __   __ _  ___  ___  _ __  
 / _` | | | | '_ \ / _` |/ _ \/ _ \| '_ \ 
| (_| | |_| | | | | (_| |  __/ (_) | | | |
 \__,_|\__,_|_| |_|\__, |\___|\___/|_| |_|
                   |___/ (c)2023 Petrofang                  
""")

DEBUG=False
INFO=False
PROMPT='\n >> '
def debug(message): print(f'{__name__} DEBUG: {message}') if DEBUG else None
def info(message): print(f'INFO: {message}') if INFO else None
debug(f'{DEBUG}')
info(f'{INFO}')
    
def main():
    from commands import CommandList
    while True:
        user_input = input(PROMPT).lower()
        if user_input:
            command, *args = user_input.split()
            command = getattr(CommandList, command, None)
            if command: 
                command(*args, me=me) if args else command(me=me)
            else: print(f'Unknown command "{user_input}".')
        else: print('Huh?')

if __name__=='__main__': 
    splash_screen()
    # prepare rooms
    from rooms import Room
    workshop=Room("Antron's Workshop", "A cottage contains a small but messy workshop of various projects in varying states of incompletion.")
    outside=Room("Potter's Field", 'The "Potter\'s field" is a place where potters have dug for clay, and thus a place conveniently full of trenches and holes for the burial of strangers.')
    workshop.exits['south']     = outside
    outside.exits['north']      = workshop

    # load or generate a character:
    import players
    user_input=input('(L)oad a character or (N)ew?' + PROMPT)
    if user_input.upper() == 'L': me = players.load()
    elif user_input.upper() == 'N': me = players.new()
    else: raise UserWarning('Listen: if you cannot follow basic prompts, this game is not for you.')
    if not me.room: me.room=workshop

    # prepare mobiles
    from mobiles import Mobile
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

    # anything else before entering main game loop?
    
    main()