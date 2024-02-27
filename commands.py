DEBUG=False
def debug(message): print(f'{__name__} *** DEBUG *** {message}') if DEBUG else None
debug(f'{DEBUG}')


import actions, players, rooms
from mobiles import Mobile, MobileEquipment
from objects import Object
from typing import Union
Any = Union[Mobile, Object, None]

class CommandList():
    ''' This is the master list of all player commands. '''
    # def command(self:Mobile=None, arg:str=None, target:Any=None):
    #     ACTION="action"
    #     actions.do(self, ACTION, arg, target)     
    
    def __no_dunders(arg:str, **kwargs): 
        ''' A filter to show only public commands on the help list.'''
        return not arg.startswith('_')

    def help(self:Mobile=None, arg:str=None, target:Any=None, **kwargs):
        ''' 
        Help           - get a list of commands.
        Help <command> - show help for a command.
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

    def look(self:Mobile=None, arg:str=None, target:Any=None, **kwargs):
        ''' Look - take a look around you. '''   
        if target==None: rooms.look(self)
        
        else: rooms.look(self)
            #TODO: LOOK at other targets
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

    def drop(self:Mobile=None, arg:str=None, target:Any=None, **kwargs):
        ''' 
        drop <item> - Drop an item on the ground. 
        drop all    - Drop all items on ground.
        '''
        ACTION="drop"

        if not target:
            actions.do(self, ACTION)
        elif not self.inventory:
            print("You have anothing to drop.")
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
        title=(f'  {str(self).capitalize()}\'s Inventory  ')
        print('-'*len(title))
        print(title)
        print('-'*len(title))
        if self.inventory: 
            for each_item in self.inventory:
                print(each_item)
        else: print('None')
        print()

        title=(f'  {str(self).capitalize()}\'s Equipment  ')
        print('-'*len(title))
        print(title)
        print('-'*len(title))
        if self.inventory: 
            for each_item in self.equipment:
                print(f"{each_item.type}: {each_item}")
        else: print('None')
        return
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
            title=(f'  {str(self).capitalize()}\'s Equipment  ')
            print('-'*len(title))
            print(title)
            print('-'*len(title))
            if self.inventory: 
                for each_item in self.equipment:
                    print(f"{each_item.type}: {each_item}")
            else: print('None')
        elif target=="all":
            for item in self.inventory:
                if item.is_equipable:
                    existing_equipment = session.query(Object) \
    .join(MobileEquipment, MobileEquipment.object_id == Object.id) \
    .filter(MobileEquipment.mobile_id == self.id) \
    .filter(MobileEquipment.type == item.type).first()
                    if not existing_equipment: 
                        actions.do(self, ACTION, target=item) 
        else:
            for item in self.inventory:
                if arg in item.name: item_to_equip=item

            if not item_to_equip:
                print(f"You don't have anything like that in inventory.")
            elif not item_to_equip.is_equipable:
                print(f"You cannot equip {item_to_equip}.")
            else:
            # Check if there's an existing equipment for the specified type
                existing_equipment = session.query(Object) \
    .join(MobileEquipment, MobileEquipment.object_id == Object.id) \
    .filter(MobileEquipment.mobile_id == self.id) \
    .filter(MobileEquipment.type == item_to_equip.type).first()
                if existing_equipment: 
                    print(f"You are already have {item_to_equip.type} equipped...")
                    actions.do(self, "unequip", target=existing_equipment)
                actions.do(self, ACTION, target=item_to_equip)     


    def unequip(self:Mobile=None, arg:str=None, target:Any=None):
        """
        unequip <item>    - removes an equipped item to inventory
        """  
        ACTION="unequip"
      
        if target=="all":
            for item in self.equipment:
                actions.do(self, ACTION, target=item)
        else:
            item_to_remove = None
            for equipped_item in self.equipment:
                if target.lower() in equipped_item.name.lower():
                    item_to_remove = equipped_item
                    break
            else: return False
            
            if not item_to_remove:
                print(f"You are not equipped with any '{target}'.")
                return False
            
            else:
                actions.do(self, ACTION, target=item_to_remove)
        
        



    def go(self=None, arg=None, target=None, **kwargs): #N,NE,E,SE,S,SW,W,NW,Up,Down,Out
        ''' 
        go <direction>  - move into the next room in <direction>
        for cardinal directions you can just type the direction, eg:
        <north|east|south|west|[etc.]> or <N|NE|E|SE|S|SW|W|NW>
        '''

        if not target:
            print("Go where?")
            return False
        dir=target
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
            print(f"exit not found in direction '{dir}'")
            return False
        
        ### move player to the room in that direction ###
        from rooms import Exit, RoomMobiles
        print(f'{self.name.capitalize()} heads {dir}...')

        # Find the to_room_id from the Exits table
        from dungeon_data import session, update
        to_room_id = session.query(Exit.to_room_id) \
                        .filter(Exit.from_room_id == self.room.id) \
                        .filter(Exit.direction == dir) \
                        .scalar()  # Retrieve a single value
      
        if to_room_id:  # Check weather a matching exit was found
            session.execute(
                update(RoomMobiles)  # Update the RoomMobiles table
                .where(RoomMobiles.mobile_id == self.id)  # Identify the mobile to update
                .values(room_id=to_room_id))  # Set the new room_id
            session.commit()  # Commit the changes to the database       
        
        else:
            print(f"Exit not found in {dir} direction.")

        rooms.look(self)

    def north(self=None, arg=None, target=None):
        ''' alias for GO NORTH.'''
        CommandList.go(target='north', self=self)
    def northeast(self=None, arg=None, target=None):
        ''' alias for GO NORTHEAST.'''
        CommandList.go(target='northeast', self=self)
    def east(self=None, arg=None, target=None):
        ''' alias for GO EAST.'''
        CommandList.go(target='east', self=self)
    def southeast(self=None, arg=None, target=None):
        ''' alias for GO SOUTHEAST.'''
        CommandList.go(target='southeast', self=self)
    def south(self=None, arg=None, target=None):
        ''' alias for GO SOUTH.'''
        CommandList.go(target='south', self=self)
    def southwest(self=None, arg=None, target=None):
        ''' alias for GO SOUTHWEST.'''
        CommandList.go(target='southwest', self=self)
    def west(self=None, arg=None, target=None):
        ''' alias for GO WEST.'''
        CommandList.go(target='west', self=self)
    def northwest(self=None, arg=None, target=None):
        ''' alias for GO NORTHWEST'''
        CommandList.go(target='northwest', self=self)
    def up(self=None, arg=None, target=None):
        ''' alias for GO UP.'''
        CommandList.go(target='up', self=self)
    def down(self=None, arg=None, target=None):
        ''' alias for GO DOWN.'''
        CommandList.go(target='down', self=self)
    d=down
    n=north
    ne=northeast
    e=east
    se=southeast
    s=south
    sw=southwest
    w=west
    nw=northwest
      
    def quit(self=None, **kwargs):
        # TODO: close game gracefully
        ''' 
        quit    - quit the game.

        Ctrl-C to close the game.
        '''

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

    def fight(self=None, arg=None, **kwargs):
        ''' fight <target> - Initiate combat.'''
        ACTION="fight"
        if not arg: print("Who would you like to attack?")
        elif not self.room.mobiles: print("There is no one you can attack.")
        else:
            target=find_target(self, arg, Mobile)
            if target: actions.do(self, ACTION, target=target)
            else: print(f'There is no {arg} here.')
    kill=fight
    attack=fight

def parse(myself, user_input=None) -> bool:
    if not user_input: print('Huh?')      
    else:
        self=myself
        command, *args = user_input.split()  
        arg = " ".join(args) if args else None
        target=arg ### TODO: refine target aquisition
        # in the meantime, send target & arg as same variable
        command_action = getattr(CommandList, command, None)
        if command_action: 
            debug(f"command={command}(self={self}, arg={arg.__repr__()}, target={target.__repr__()})")
            command_action(self=self, arg=arg, target=target)
        else: print(f'Unknown command "{command}".')

def find_target(self:Mobile, target_name:str, type:Any=None) -> Any:
    """
    search inventory and room for target Object of Mobile
    """
    if type != Object: 
        for mobile in self.room.mobiles:
            if target_name in mobile.name: return mobile
    elif type != Mobile: 
        for item in self.inventory:
            if target_name in item.name: return item
        for item in self.room.inventory:
            if target_name in item.name: return item
    else: return None