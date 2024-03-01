DEBUG=False
def debug(message): print(f'{__name__} *** DEBUG *** {message}') if DEBUG else None
debug(f'{DEBUG}')

import actions, players, rooms
from mobiles import Mobile, MobileEquipment
from objects import Object
from typing import Union
Target = Union[Mobile, Object]

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
    
    def command(self:Mobile=None, arg:str=None, target:Target=None):
        """ 
        docstring - displayed by help <command>
        """
        ACTION="action"
        # command logic
        actions.do(self, ACTION, arg, target)     
    '''

    def __no_dunders(arg:str, **kwargs): 
        ''' A filter to show only public commands on the help list.'''
        return not arg.startswith('_')

    def help(self:Mobile=None, arg:str=None, target:Target=None, **kwargs):
        ''' 
        help           - get a list of commands.
        help <command> - show help for a command.
        '''
        list_of_commands = sorted(filter(CommandList.__no_dunders, vars(CommandList)))
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

    def look(self:Mobile=None, arg:str=None, **kwargs):
        """
        look        - look at your surroundings
        look <target>  - look at target
        """   
        if arg==None: self.room.look(self)
        else:
            target=find_target(self, arg)
            if target is not None:
                target.look()
            elif self.room.exit(arg): 
                self.room.exit(arg).look()
            else:
                print(f"You see no '{arg}'.")
    l=look

    def get(self:Mobile=None, arg:str=None, target:Object=None, **kwargs):
        """
        get <item> - get an item from the room.
        get all    - get all items from the room.
        """  
        ACTION="get"  
        if not arg:
            print("Get what?")
        elif not self.room.inventory:
            print("There is nothing here to get.")
        elif arg=="all":
            for item in self.room.inventory:
                actions.do(self, ACTION, target=item)
        else:
            item=None
            for target in self.room.inventory:
                if arg in target.name:
                    item=target
                    break
            if item is None:
                print(f"Unable to locate '{arg}.'")
            else:
                actions.do(self, ACTION, target=item)

    def drop(self:Mobile=None, arg:str=None, target:Target=None, **kwargs):
        ''' 
        drop <item> - Drop an item on the ground. 
        drop all    - Drop all items on ground.
        '''
        ACTION="drop"

        if not target: # just.. DROP!  
            print("You drop down on one knee.")
        elif not self.inventory:
            print("You have nothing to drop.")
        elif arg=="all":
            for item in self.inventory: 
                actions.do(self, ACTION, target=item)
        else:
            item=None    
            for each_item in self.inventory:
                if arg in each_item.name: item = each_item
            if item is not None:
                actions.do(self, ACTION, target=item)
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
        ACTION="equip"
    
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
                        actions.do(self, ACTION, target=item) 
                        equips+=1
            
            if equips==0:print(f"You're already equipped everything you can...")
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
                    n="" 
                    if item_to_equip.type[0] in "aeiou": n="n"
                    print(f"You are already have a{n} {item_to_equip.type} equipped...")
                    actions.do(self, "unequip", target=self.equipment[item.type])
                actions.do(self, ACTION, target=item_to_equip)     
    wear=equip  #TODO only if type not 'weapon'
    wield=equip #TODO only if type is 'weapon'

    def unequip(self:Mobile=None, arg:str=None, target:Target=None):
        """
        unequip <item>    - removes an equipped item to inventory
        """  
        ACTION="unequip"
      
        if target=="all":
            for item in self.equipment.values():
                if item: actions.do(self, ACTION, target=item)
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
                actions.do(self, ACTION, target=item_to_remove)
    remove=unequip  #TODO: only if type not 'weapon'

    def go(self, arg=None, target=None, **kwargs): 
        """ 
        go <direction>  - move into the next room in <direction>
        for cardinal directions you can just type the direction, eg:
        <north|east|south|west|[etc.]> or <N|NE|E|SE|S|SW|W|NW>
        """
        ACTION="go"
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

        actions.do(self, ACTION, dir)


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
        ''' 
        open <exit> - opens a closed exit by direction or key word.
        '''
        # TODO: containers
        ACTION = "open_door"
        if arg:
            if self.room.exit(arg):
                actions.do(self, ACTION, arg, self.room.exit(arg))

    def close(self=None, arg=None, **kwargs):
        ''' 
        close <exit> - opens a closed exit by direction or key word.
        '''
        # TODO: containers
        ACTION = "close_door"
        if arg:
            if self.room.exit(arg):
                actions.do(self, ACTION, arg, self.room.exit(arg))


    def quit(self=None, **kwargs):
        ''' 
        quit    - quit the game.

        Ctrl-C to close the game.
        '''
        # TODO: close game gracefully
       
        players.unload(self)
        print("Ctrl-C to close")
        exit()
    q=quit

    def say(self, arg=None, **kwargs):
        ''' say - say something'''
        ACTION = "say"
        if arg:
            actions.do(self, ACTION, arg)
        else: print("Say what?")

    def fight(self=None, target=None, **kwargs):
        ''' fight <target> - Initiate combat.'''
        ACTION="fight"
        if not target: print("Who would you like to attack?")
        elif not self.room.mobiles: print("There is no one you can attack.")
        else:
            target=find_target(self, target, Mobile)
            if target: actions.do(self, ACTION, target=target)
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
    if not user_input: print('Huh?')      
    else:
        user_input=user_input.lower()
        command, *args = user_input.split()  
        arg = " ".join(args) if args else None
        target=arg #target aquisition is handled by each command handler
        command_action = getattr(CommandList, command, None)
        if command_action: 
            debug(f"command={command}(self={myself}, arg={arg.__repr__()}, target={target.__repr__()})")
            command_action(self=myself, arg=arg, target=target)
        else: print(f'Unknown command "{command}".')

def find_target(self:Mobile, arg:str, type:Target=None, room_first=True, inv_first=False) -> Target:
    """
    search inventory and room for target Object or Mobile
    """
    debug(f"find_target('{arg}')")
    target = None
    if type != Object: 
        for mobile in self.room.mobiles:
            if arg in mobile.name and mobile is not self: 
                return mobile
    if type !=Mobile: 
        if room_first and not inv_first:
            for item in self.inventory:
                if arg in item.name: 
                    return item
            for item in self.room.inventory:
                if arg in item.name:    
                    return item
        else:
            for item in self.room.inventory:
                if arg in item.name:  
                    return item
            for item in self.inventory:
                if arg in item.name: 
                    return item
    else:
        debug(f"'{arg}' not found in {self}.room or .inventory.")
        return None