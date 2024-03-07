import actions, players
from mobiles import Mobile 
from objects import Object

class CommandList():
    ''' 
    This is the master list of all player commands outside of combat,
    as well as being the command handler for each command.
    
    The command handlers further parse and sanitize command arguments,
    then determine the target with find_target() before sending 
    SAAT (Subject, Action, Arguments, Target) to be performed by the
    actions module (actions.py) with:
        actions.do(S,A,A,T)

    Generally speaking, commands which do not change anything or cause
    any interaction with other game objects, mobiles or players can
    be parsed directly by the command and are not sent to do(SAAT).
        eg., checking inventory or looking.
    
    format:
    
    def command(subject:Mobile=None, arg:str=None, target=None):
        """ 
        docstring - displayed by help <command>
        """
        action="action"
        # command logic
        actions.do(subject, action, arg, target)     
    '''

    def __no_dunders(arg:str, **kwargs): 
        ''' A filter to show only public commands on the help list.'''
        return not arg.startswith('_')

    def help(subject:Mobile = None, arg:str = None, target=None, **kwargs):
        ''' 
        help           - get a list of commands.
        help <command> - show help for a command.
        '''
        list_of_commands = sorted(filter(CommandList.__no_dunders, 
                                         vars(CommandList)))
        if arg == None:
            subject.print(CommandList.help.__doc__)
            subject.print(' --- Command List ---')
            for each in list_of_commands:
                subject.print(f'    {each}',end=' ')
            subject.print()
        elif arg in list_of_commands:
            help_command = getattr(CommandList, arg)
            subject.print(help_command.__doc__)       
        else: subject.print(f'Unknown command "{arg}".')

    def look(subject:Mobile = None, arg:str = None, **kwargs):
        """
        look - look at your surroundings
        look <target> - look at target
        look in <container> - look inside a container 
        """
        if arg==None: 
            subject.room.look(subject)
        elif arg.startswith("in "):
            arg=arg[3:]
            target=find_target(subject, arg, Object, in_room=True, in_inventory=True)
            if target and target.type == "container":
                target.look_in(subject)
            else:
                subject.print("You cannot see inside that.")
        elif subject.room.signs and arg in subject.room.signs.keys():
            subject.print(subject.room.signs[arg])
        else:
            target=find_target(subject, arg, in_room=True, 
                               in_inventory=True, in_equipment=True)
            if target is not None:
                target.look(subject)
            elif subject.room.exit(arg): 
                subject.room.exit(arg).look(subject)
            else:
                subject.print(f"You see no '{arg}'.")
    l=look

    def put(subject:Mobile=None, arg:str=None, target:Object=None, **kwargs):
        """
        put <item> in <container> - put an item from the container.
        """  
        action="put"  
        if not arg:
            subject.print("Put what in what?")
        else:
            targets=arg.split(" in ", 1)
            if len(targets) == 2:
                targets = [target.strip() for target in targets]
                item = find_target(subject, targets[0], type=Object,
                                         in_inventory=True)
                container = find_target(subject, targets[1], type=Object, 
                                         in_inventory=True, in_room=True)
                if item and container:
                    actions.do(subject, action, container, item)
                else:
                    subject.print("Put what in what now?")

    def get(subject:Mobile=None, arg:str=None, target:Object=None, **kwargs):
        """
        get <item> - get an item from the room.
        get all    - get all items from the room.
        get <item> from <container> - get an item from a container.
        """  
        action="get"  
        if not arg:
            # get
            subject.print("Get what?")
        elif not subject.room.inventory:
            subject.print("There is nothing here to get.")
        elif arg=="all":
            # get all
            for item in subject.room.inventory:
                actions.do(subject, action, target=item)
        elif " from " in arg:
            # get <item> from <container>
            targets=arg.split(" from ", 1)
            if len(targets) == 2:
                targets = [target.strip() for target in targets]
                item = find_target(subject, targets[0], 
                                   type=Object, in_containers=True)
                container = find_target(subject, targets[1], type=Object, 
                                        in_inventory=True, in_room=True)
                if item and container:
                    actions.do(subject, action, container, item)
                else:
                    subject.print("Put what in what now?")
        else:
            # get <item>
            item=find_target(subject, arg, Object, in_room=True)
            if item:
                actions.do(subject, action, target=item)
            else:
                subject.print(f"Unable to find '{arg}'.")

    def drop(subject:Mobile = None, arg:str = None, target=None, **kwargs):
        ''' 
        drop <item> - Drop an item on the ground. 
        drop all    - Drop all items on ground.
        '''
        action="drop"

        if not target: # just.. DROP!  
            action.echo_at(subject, "You drop down on one knee.")
            action.echo_around(subject, f"{subject} drops down on one knee.")
        elif not subject.inventory:
            subject.print("You have nothing to drop.")
        elif arg=="all":
            for item in subject.inventory: 
                actions.do(subject, action, target=item)
        else:
            item=None    
            for each_item in subject.inventory:
                if arg in each_item.name: item = each_item
            if item is not None:
                actions.do(subject, action, target=item)
            else:     
                subject.print(f"'{target.capitalize()}' not found in inventory.")
    
    def inventory(subject:Mobile=None, **kwargs):
        ''' 
        inventory   - Check inventory and equipment. 
        inv         -
        '''
        # list equipped items:
        CommandList.equip(subject)

        # list inventory items:
        title=(f'  {str(subject).capitalize()}\'s Inventory  ')
        title=f'{title:^30}'
        subject.print('-'*len(title))
        subject.print(title)
        subject.print('-'*len(title))
        if subject.inventory: 
            for each_item in subject.inventory:
                subject.print(each_item)
        else: subject.print('None')
        subject.print()
    inv=inventory

    def equip(subject:Mobile=None, arg:str=None, target:Object=None):
        """
        equip <item>    - equips an item in inventory
        equip           - lists equipped items
        """
        action="equip"
    
        # find the item in inventory
        from dungeon_data import session
        item_to_equip=None
        if not target:
            title=f'{str(subject).capitalize()}\'s Equipment'
            title=f'{title:^30}'
            subject.print(f'-'*len(title))
            subject.print(title)
            subject.print(f'-'*len(title))
            for slot, item in subject.equipment.items():
                subject.print(f"{slot:10}:  {item}")
            return
        elif target=="all":
            equips=0
            for item in subject.inventory:
            
                if item.is_equipable:
                    if not subject.equipment[item.type]: 
                        actions.do(subject, action, target=item) 
                        equips+=1
            
            if equips==0:print(f"You're already equipped everything you can.")
        else:   
            for item in subject.inventory:
                if arg in item.name: item_to_equip=item
            if not item_to_equip:
                subject.print(f"You don't have anything like that in inventory.")
            elif not item_to_equip.is_equipable:
                subject.print(f"You cannot equip {item_to_equip}.")
            else:
            # Check if there's an existing equipment for the specified type
                
                if subject.equipment[item.type]:
                    n = "n" if item_to_equip.type[0] in "aeiou" else ""
                    subject.print(f"You are already have a{n}",
                          f"{item_to_equip.type} equipped...")
                    actions.do(subject, "unequip", 
                               target=subject.equipment[item.type])
                actions.do(subject, action, target=item_to_equip)     
    wear=equip  #TODO only if type not 'weapon'
    wield=equip #TODO only if type is 'weapon'

    def unequip(subject:Mobile = None, arg:str = None, target=None):
        """
        unequip <item>    - removes an equipped item to inventory
        """  
        action="unequip"
      
        if target=="all":
            for item in subject.equipment.values():
                if item: actions.do(subject, action, target=item)
        else:
            item_to_remove = None
            for equipped_item in subject.equipment.values():
                if equipped_item:
                    if target.lower() in equipped_item.name.lower():
                        item_to_remove = equipped_item
                        break
            else: return False
            
            if not item_to_remove:
                subject.print(f"You are not equipped with any '{target}'.")
                return False
            
            else:
                actions.do(subject, action, target=item_to_remove)
    remove = unequip  #TODO: only if type not 'weapon'

    def go(subject, arg=None, target=None, **kwargs): 
        """ 
        go <direction>  - move into the next room in <direction>
        for cardinal directions you can just type the direction, eg:
        <north|east|south|west|[etc.]> or <N|NE|E|SE|S|SW|W|NW>
        """
        action="go"
        if not arg:
            subject.print("Go where?")
            return False
        dir=arg
        if dir=='n':dir='north'
        if dir=='ne':dir='northeast'
        if dir=='e':dir='east'
        if dir=='se': dir='southeast'
        if dir=='s':dir='south'
        if dir=='sw':dir='southwest'
        if dir=='w':dir='west'
        if dir=='nw':dir='northwest'
        for exit in subject.room.exits:
            if exit.direction==dir: break
        else: 
            subject.print(f"Exit not found in direction '{dir}'")
            return False

        actions.do(subject, action, dir)


    def north(subject=None, arg=None, target=None):
        ''' alias for GO NORTH.'''
        CommandList.go(arg='north', subject=subject)
    def northeast(subject=None, arg=None, target=None):
        ''' alias for GO NORTHEAST.'''
        CommandList.go(arg='northeast', subject=subject)
    def east(subject=None, arg=None, target=None):
        ''' alias for GO EAST.'''
        CommandList.go(arg='east', subject=subject)
    def southeast(subject=None, arg=None, target=None):
        ''' alias for GO SOUTHEAST.'''
        CommandList.go(arg='southeast', subject=subject)
    def south(subject=None, arg=None, target=None):
        ''' alias for GO SOUTH.'''
        CommandList.go(arg='south', subject=subject)
    def southwest(subject=None, arg=None, target=None):
        ''' alias for GO SOUTHWEST.'''
        CommandList.go(arg='southwest', subject=subject)
    def west(subject=None, arg=None, target=None):
        ''' alias for GO WEST.'''
        CommandList.go(arg='west', subject=subject)
    def northwest(subject=None, arg=None, target=None):
        ''' alias for GO NORTHWEST'''
        CommandList.go(arg='northwest', subject=subject)
    def up(subject=None, arg=None, target=None):
        ''' alias for GO UP.'''
        CommandList.go(arg='up', subject=subject)
    def down(subject=None, arg=None, target=None):
        ''' alias for GO DOWN.'''
        CommandList.go(arg='down', subject=subject)
    def out(subject=None, arg=None, target=None):
        ''' alias for GO OUT.'''
        CommandList.go(arg='out', subject=subject)
    d=down
    n=north
    ne=northeast
    e=east
    se=southeast
    s=south
    sw=southwest
    w=west
    nw=northwest
      
    def open(subject=None, arg=None, **kwargs):
        """ 
        open <exit> - opens a closed exit by direction or key word.
        open <container> - opens a container
        """
        if not arg:
            subject.print("Open what?")
        elif subject.room.exit(arg):
            exit = subject.room.exit(arg)
            # it's an exit:
            if not exit.is_door:
                subject.print(f"The {exit.way}{exit.direction} cannot be opened.")
            elif exit.is_open:
                subject.print(f"The {exit.way}{exit.direction} is already open.")
            elif exit.is_locked:
                actions.echo_at(subject, 
                    f"You try to open the {exit.way}{exit.direction}, but it is locked.")
                actions.echo_around(subject,
                    f"{subject} tries to open the {exit.way}{exit.direction}, but it is locked.")
            else:  
                actions.do(subject, "open_door", arg, subject.room.exit(arg))
             
        else:
            container = find_target(subject, arg, Object, 
                                    in_room=True, in_inventory=True)    
            if container:
                if container.type == "container":
                    print(f"container '{container}' cannot be opened yet")
                    # TODO:
                    #   if container.is_open==False and container.is_locked==False:
                    #       actions.do(subject, "open_container", None, container)
                else: 
                    subject.print(f"{container} cannot be opened.")
            else:
                subject.print(f"Couldn't find '{arg}'")


    def close(subject=None, arg=None, **kwargs):
        """
        close <exit> - opens a closed exit by direction or key word.
        """
        if arg:
            if subject.room.exit(arg): # if it is an exit
                exit=subject.room.exit(arg)
                if exit.is_door: # if it is a door
                    if not exit.is_open: # is it is open
                        actions.do(subject, "close_door", exit, exit)
                    else:
                        subject.print(f"The {exit.way}{exit.direction} is already closed.")
                else: # not a door:
                    subject.print(f"The {exit.way}{exit.direction} cannot be closed.")
            else: # not an exit, check for containers:
                container = find_target(subject, arg, Object,
                                        in_room=True, in_inventory=True)
                if container:
                    if container.type == "container":
                        print(f"container '{container}' cannot be closed yet")
                        # TODO:
                        #   if container.is_open==True:
                        #       actions.do(subject, "close_container", None, container)
                    else: 
                        subject.print(f"{container} cannot be closed.")
                else:
                    subject.print(f"Couldn't find '{arg}'")

    def quit(subject=None, **kwargs):
        """
        quit    - save and quit the game.
        """
        # TODO: close game gracefully
       
        players.unload(subject)
    q=quit

    def say(subject, arg=None, **kwargs):
        ''' say - say something'''
        action = "say"
        if arg:
            actions.do(subject, action, arg)
        else: subject.print("Say what?")

    def fight(subject=None, arg=None, **kwargs):
        ''' fight <target> - Initiate combat.'''
        action="fight"
        if not arg: 
            subject.print("Who would you like to attack?")
        elif not subject.room.mobiles: 
            subject.print("There is no one you can attack.")
        else:
            target=find_target(subject, arg, Mobile)
            if target: 
                actions.do(subject, action, target=target)
            else: 
                subject.print(f'There is no {target} here.')
    kill=fight
    attack=fight


def parse(myself, user_input=None) -> bool:
    """
    This is the command parser, the first link in the chain of command
    where player input is parsed and converted into game action. Here,
    user input is split into a command and an argument. Then, the command
    is checked against the CommandList and (if a command is found) the
    argument is sent for further parsing, sanitizing, and execution.
    """
    if not user_input: 
        myself.print('Huh?\n')      
    else:
        myself.print()
        user_input=user_input.lower()
        if myself.room.commands and myself.room.commands.get(user_input):
            myself.room.command(myself, user_input)
        else:
            command, *args = user_input.split()  
            arg = " ".join(args) if args else None
            target=arg #target aquisition is handled by each command handler
            command_action = getattr(CommandList, command, None)
            if command_action: 
                command_action(subject=myself, arg=arg, target=target)
            else: 
                myself.print(f'Unknown command "{command}".')

def find_target(myself:Mobile, arg:str, type=None, in_room=False, in_inventory=False,
                in_equipment=False, in_exits=False, in_containers=False, **kwargs):
    """
    This function searches for a target item, mobile, or exit by keyword 
    and returns the game object if found, or None. 
        arguments:
            myself - the player with whom the search is associated
            arg - the keyword or name of the item being searched
            type - Object, Mobile, or None, where None means either/both
            in_room - search in the player's room. If type=Mobile, the
                room will be searched even if in_room=False
            in_inventory - search in the player's inventory.
            in_equipment - search in the player's equipment.
            in_containers - search in containers in myself's room and inventory.
            in_exits - search for exits in the player's room.
    """
    # TODO: fuzzywuzzy? .like()?
    target = None
    if type is Mobile or type is None: # not an object
        for mobile in myself.room.mobiles:
            if mobile.name.startswith(arg) and mobile is not myself: 
                target = mobile
            else:
                names=mobile.name.split()
                for name in names:
                    if name.startswith(arg):
                        target = mobile
        if target: return target
    if type is Object or type is None: # and if it's not a mobile it must be an object or None
        if in_room:
            for item in myself.room.inventory:
                if item.name.startswith(arg):    
                    target = item
                else:
                    names=item.name.split()
                    for name in names:
                        if name.startswith(arg):
                            target = item
            if target: return target            
        if in_inventory:
            for item in myself.inventory:
                if item.name.startswith(arg): 
                    target = item
                else:
                    names=item.name.split()
                    for name in names:
                        if name.startswith(arg):
                            target = item
            if target: return target
        if in_equipment:
            for item in [item for item in myself.equipment.values() if item is not None]:
                if item.name.startswith(arg): 
                    target = item
                else:
                    names=item.name.split()
                    for name in names:
                        if name.startswith(arg):
                            target = item
            if target: return target
        if in_containers:
            for item in myself.room.inventory:
                if item.contents:
                    for thing in item.contents:
                        if thing.name.startswith(arg):
                            target=thing
            if target: return target
            for item in myself.inventory:
                if item.contents:
                    for thing in item.contents:
                        if thing.name.startswith(arg):
                            target=thing
            if target: return 

    if type is None:                        
        if in_exits:
            for exit in myself.room.exits:
                if exit.direction == arg:
                    target = exit
        return target
    return target
