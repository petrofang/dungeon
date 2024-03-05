import actions, players
from mobiles import Mobile 
from objects import Object
from typing import Union

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
    
    def command(self:Mobile=None, arg:str=None, target=None):
        """ 
        docstring - displayed by help <command>
        """
        action="action"
        # command logic
        actions.do(self, action, arg, target)     
    '''

    def __no_dunders(arg:str, **kwargs): 
        ''' A filter to show only public commands on the help list.'''
        return not arg.startswith('_')

    def help(self:Mobile = None, arg:str = None, target=None, **kwargs):
        ''' 
        help           - get a list of commands.
        help <command> - show help for a command.
        '''
        list_of_commands = sorted(filter(CommandList.__no_dunders, 
                                         vars(CommandList)))
        if arg == None:
            print(CommandList.help.__doc__)
            print(' --- Command List ---')
            for each in list_of_commands:
                print(f'    {each}',end=' ')
            print()
        elif arg in list_of_commands:
            help_command = getattr(CommandList, arg)
            print(help_command.__doc__)       
        else: print(f'Unknown command "{arg}".')

    def look(self:Mobile = None, arg:str = None, **kwargs):
        """
        look - look at your surroundings
        look <target> - look at target
        look in <container> - look inside a container 
        """
        if arg==None: 
            self.room.look(self)
        elif arg.startswith("in "):
            arg=arg[3:]
            target=find_target(self, arg, Object, in_room=True, in_inventory=True)
            if target and target.type == "container":
                target.look_in()
            else:
                print("You cannot see inside that.")
        elif self.room.signs and arg in self.room.signs.keys():
            print(self.room.signs[arg])
        else:
            target=find_target(self, arg, in_room=True, in_inventory=True, in_equipment=True)
            if target is not None:
                target.look()
            elif self.room.exit(arg): 
                self.room.exit(arg).look()
            else:
                print(f"You see no '{arg}'.")
    l=look

    def put(self:Mobile=None, arg:str=None, target:Object=None, **kwargs):
        """
        put <item> in <container> - put an item from the container.
        """  
        action="put"  
        if not arg:
            print("Put what in what?")
        else:
            targets=arg.split(" in ", 1)
            if len(targets) == 2:
                targets = [target.strip() for target in targets]
                item = find_target(self, targets[0], type=Object,
                                         in_inventory=True)
                container = find_target(self, targets[1], type=Object, 
                                         in_inventory=True, in_room=True)
                if item and container:
                    actions.do(self, action, container, item)
                else:
                    print("Put what in what now?")

    def get(self:Mobile=None, arg:str=None, target:Object=None, **kwargs):
        """
        get <item> - get an item from the room.
        get all    - get all items from the room.
        get <item> from <container> - get an item from a container.
        """  
        action="get"  
        if not arg:
            # get
            print("Get what?")
        elif not self.room.inventory:
            print("There is nothing here to get.")
        elif arg=="all":
            # get all
            for item in self.room.inventory:
                actions.do(self, action, target=item)
        elif " from " in arg:
            # get <item> from <container>
            targets=arg.split(" from ", 1)
            if len(targets) == 2:
                targets = [target.strip() for target in targets]
                item = find_target(self, targets[0], 
                                   type=Object, in_containers=True)
                container = find_target(self, targets[1], type=Object, 
                                        in_inventory=True, in_room=True)
                if item and container:
                    actions.do(self, action, container, item)
                else:
                    print("Put what in what now?")
        else:
            # get <item>
            item=find_target(self, arg, Object, in_room=True)
            if item:
                actions.do(self, action, target=item)
            else:
                print(f"Unable to find '{arg}'.")

    def drop(self:Mobile = None, arg:str = None, target=None, **kwargs):
        ''' 
        drop <item> - Drop an item on the ground. 
        drop all    - Drop all items on ground.
        '''
        action="drop"

        if not target: # just.. DROP!  
            print("You drop down on one knee.")
        elif not self.inventory:
            print("You have nothing to drop.")
        elif arg=="all":
            for item in self.inventory: 
                actions.do(self, action, target=item)
        else:
            item=None    
            for each_item in self.inventory:
                if arg in each_item.name: item = each_item
            if item is not None:
                actions.do(self, action, target=item)
            else:     
                print(f"'{target.capitalize()}' not found in inventory.")
    
    def inventory(self:Mobile=None, **kwargs):
        ''' 
        inventory   - Check inventory and equipment. 
        inv         -
        '''
        # list equipped items:
        CommandList.equip(self)

        # list inventory items:
        title=(f'  {str(self).capitalize()}\'s Inventory  ')
        title=f'{title:^30}'
        print('-'*len(title))
        print(title)
        print('-'*len(title))
        if self.inventory: 
            for each_item in self.inventory:
                print(each_item)
        else: print('None')
        print()

    inv=inventory

    def equip(self:Mobile=None, arg:str=None, target:Object=None):
        """
        equip <item>    - equips an item in inventory
        equip           - lists equipped items
        """
        action="equip"
    
        # find the item in inventory
        from dungeon_data import session
        item_to_equip=None
        if not target:
            title=f'{str(self).capitalize()}\'s Equipment'
            title=f'{title:^30}'
            print(f'-'*len(title))
            print(title)
            print(f'-'*len(title))
            for slot, item in self.equipment.items():
                print(f"{slot:10}:  {item}")
            return
        elif target=="all":
            equips=0
            for item in self.inventory:
            
                if item.is_equipable:
                    if not self.equipment[item.type]: 
                        actions.do(self, action, target=item) 
                        equips+=1
            
            if equips==0:print(f"You're already equipped everything you can.")
        else:   
            for item in self.inventory:
                if arg in item.name: item_to_equip=item
            if not item_to_equip:
                print(f"You don't have anything like that in inventory.")
            elif not item_to_equip.is_equipable:
                print(f"You cannot equip {item_to_equip}.")
            else:
            # Check if there's an existing equipment for the specified type
                
                if self.equipment[item.type]:
                    n = "n" if item_to_equip.type[0] in "aeiou" else ""
                    print(f"You are already have a{n}",
                          f"{item_to_equip.type} equipped...")
                    actions.do(self, "unequip", 
                               target=self.equipment[item.type])
                actions.do(self, action, target=item_to_equip)     
    wear=equip  #TODO only if type not 'weapon'
    wield=equip #TODO only if type is 'weapon'

    def unequip(self:Mobile = None, arg:str = None, target=None):
        """
        unequip <item>    - removes an equipped item to inventory
        """  
        action="unequip"
      
        if target=="all":
            for item in self.equipment.values():
                if item: actions.do(self, action, target=item)
        else:
            item_to_remove = None
            for equipped_item in self.equipment.values():
                if equipped_item:
                    if target.lower() in equipped_item.name.lower():
                        item_to_remove = equipped_item
                        break
            else: return False
            
            if not item_to_remove:
                print(f"You are not equipped with any '{target}'.")
                return False
            
            else:
                actions.do(self, action, target=item_to_remove)
    remove=unequip  #TODO: only if type not 'weapon'

    def go(self, arg=None, target=None, **kwargs): 
        """ 
        go <direction>  - move into the next room in <direction>
        for cardinal directions you can just type the direction, eg:
        <north|east|south|west|[etc.]> or <N|NE|E|SE|S|SW|W|NW>
        """
        action="go"
        if not arg:
            print("Go where?")
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
        for exit in self.room.exits:
            if exit.direction==dir: break
        else: 
            print(f"Exit not found in direction '{dir}'")
            return False

        actions.do(self, action, dir)


    def north(self=None, arg=None, target=None):
        ''' alias for GO NORTH.'''
        CommandList.go(arg='north', self=self)
    def northeast(self=None, arg=None, target=None):
        ''' alias for GO NORTHEAST.'''
        CommandList.go(arg='northeast', self=self)
    def east(self=None, arg=None, target=None):
        ''' alias for GO EAST.'''
        CommandList.go(arg='east', self=self)
    def southeast(self=None, arg=None, target=None):
        ''' alias for GO SOUTHEAST.'''
        CommandList.go(arg='southeast', self=self)
    def south(self=None, arg=None, target=None):
        ''' alias for GO SOUTH.'''
        CommandList.go(arg='south', self=self)
    def southwest(self=None, arg=None, target=None):
        ''' alias for GO SOUTHWEST.'''
        CommandList.go(arg='southwest', self=self)
    def west(self=None, arg=None, target=None):
        ''' alias for GO WEST.'''
        CommandList.go(arg='west', self=self)
    def northwest(self=None, arg=None, target=None):
        ''' alias for GO NORTHWEST'''
        CommandList.go(arg='northwest', self=self)
    def up(self=None, arg=None, target=None):
        ''' alias for GO UP.'''
        CommandList.go(arg='up', self=self)
    def down(self=None, arg=None, target=None):
        ''' alias for GO DOWN.'''
        CommandList.go(arg='down', self=self)
    def out(self=None, arg=None, target=None):
        ''' alias for GO OUT.'''
        CommandList.go(arg='out', self=self)
    d=down
    n=north
    ne=northeast
    e=east
    se=southeast
    s=south
    sw=southwest
    w=west
    nw=northwest
      
    def open(self=None, arg=None, **kwargs):
        """ 
        open <exit> - opens a closed exit by direction or key word.
        """
        if arg:
            if self.room.exit(arg):
                if self.room.exit(arg # a closed, unlocked door:
                        ).is_door and not self.room.exit(arg
                        ).is_open and not self.room.exit(arg
                        ).is_locked:  
                    actions.do(self, "open_door", arg, self.room.exit(arg))
                else: print(f"The '{arg}' cannot be opened.")
            else: 
                pass
                # TODO: containers
        else:
            print("Open what?")

    def close(self=None, arg=None, **kwargs):
        """
        close <exit> - opens a closed exit by direction or key word.
        """
        if arg:
            if self.room.exit(arg):
                if self.room.exit(arg).is_door:
                    actions.do(self, "close_door", arg, self.room.exit(arg))
        # TODO: move exit.close() error checking to here.
        # TODO: containers

    def quit(self=None, **kwargs):
        """
        quit    - quit the game.

        Ctrl-C to close the game.
        """
        # TODO: close game gracefully
       
        players.unload(self)
        print("Ctrl-C to close")
        exit()
    q=quit

    def say(self, arg=None, **kwargs):
        ''' say - say something'''
        action = "say"
        if arg:
            actions.do(self, action, arg)
        else: print("Say what?")

    def fight(self=None, arg=None, **kwargs):
        ''' fight <target> - Initiate combat.'''
        action="fight"
        if not arg: print("Who would you like to attack?")
        elif not self.room.mobiles: print("There is no one you can attack.")
        else:
            target=find_target(self, arg, Mobile)
            if target: actions.do(self, action, target=target)
            else: print(f'There is no {target} here.')
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
    if not user_input: print('Huh?\n')      
    else:
        print()
        user_input=user_input.lower()
        if myself.room.commands and myself.room.commands.get(user_input):
            myself.room.command(myself, user_input)
        else:
            command, *args = user_input.split()  
            arg = " ".join(args) if args else None
            target=arg #target aquisition is handled by each command handler
            command_action = getattr(CommandList, command, None)
            if command_action: 
                command_action(self=myself, arg=arg, target=target)
            else: print(f'Unknown command "{command}".')

def find_target(self:Mobile, arg:str, type=None, in_room=False, in_inventory=False,
                in_equipment=False, in_exits=False, in_containers=False, **kwargs):
    """
    This function searches for a target item, mobile, or exit by keyword 
    and returns the game object if found, or None. 
        arguments:
            self - the player with whom the search is associated
            arg - the keyword or name of the item being searched
            type - Object, Mobile, or None, where None means either/both
            in_room - search in the player's room. If type=Mobile, the
                room will be searched even if in_room=False
            in_inventory - search in the player's inventory.
            in_equipment - search in the player's equipment.
            in_containers - search in containers in self room and inventory.
            in_exits - search for exits in the player's room.
    """
    # TODO: fuzzywuzzy? .like()?
    target = None
    if type is Mobile or type is None: # If it's not an object it must be a Mobile
        for mobile in self.room.mobiles:
            if mobile.name.startswith(arg) and mobile is not self: 
                target = mobile
            else:
                names=mobile.name.split()
                for name in names:
                    if name.startswith(arg):
                        target = mobile
        if target: return target
    if type is Object or type is None: # and if it's not a mobile it must be an object or None
        if in_room:
            for item in self.room.inventory:
                if item.name.startswith(arg):    
                    target = item
                else:
                    names=item.name.split()
                    for name in names:
                        if name.startswith(arg):
                            target = item
            if target: return target            
        if in_inventory:
            for item in self.inventory:
                if item.name.startswith(arg): 
                    target = item
                else:
                    names=item.name.split()
                    for name in names:
                        if name.startswith(arg):
                            target = item
            if target: return target
        if in_equipment:
            for item in [item for item in self.equipment.values() if item is not None]:
                if item.name.startswith(arg): 
                    target = item
                else:
                    names=item.name.split()
                    for name in names:
                        if name.startswith(arg):
                            target = item
            if target: return target
        if in_containers:
            for item in self.room.inventory:
                if item.contents:
                    for thing in item.contents:
                        if thing.name.startswith(arg):
                            target=thing
            if target: return target
            for item in self.inventory:
                if item.contents:
                    for thing in item.contents:
                        if thing.name.startswith(arg):
                            target=thing
            if target: return 

    if type is None:                        
        if in_exits:
            for exit in self.room.exits:
                if exit.direction == arg:
                    target = exit
        return target
    return target
