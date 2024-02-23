#commands.py
DEBUG=False
def debug(message): print(f'{__name__} *** DEBUG *** {message}') if DEBUG else None
debug(f'{DEBUG}')

import rooms
from dungeon_data import session, update
from players import PlayerCharacter
from mobiles import MobileInventory, MobileEquipment, Mobile
from objects import Object, ItemTypes
from rooms import RoomInventory



class CommandList():
    ''' This is the master list of all player commands. 

    Usage: 

command, *args = input().split()
command = getattr(CommandList, command, None)
if command: command(*args, me=player) if args else command(me=player)
'''
    def __no_dunders(command:str): 
        ''' A filter to show only public commands on the help list.'''
        return not command.startswith('_')

    def help(command=None, *args, **kwargs):
        ''' Help           - get a list of commands.
 Help <command> - show help for a command.'''
        list_of_commands = sorted(filter(CommandList.__no_dunders, vars(CommandList)))
        if command == None:
            print(CommandList.help.__doc__)
            print('\n --- Command List ---')
            for each in list_of_commands:
                print(f'    {each}')
        elif command in list_of_commands:
            command = getattr(CommandList, command)
            print(command.__doc__)        
        else: print(f'Unknown command "{command}".')

    def quit(*args, **kwargs):
        # TODO: not so unceremoniously
        ''' Quit - quit the game (without saving). '''
        quit()

    def look(target=None, me:PlayerCharacter=None):
        ''' Look - take a look at the place where you are. '''
        if target==None: rooms.look(me)
        

    def get(args, me:PlayerCharacter=None, **kwargs):
        ''' Get <item> - Get an item from the room. '''
        # TODO: "get all"
         # Join Room_Inventory with Objects to get Object instances
        room_inventory = (
            session.query(Object)
            .join(RoomInventory, RoomInventory.object_id == Object.id)
            .filter(RoomInventory.room_id == me.room_id)
            .all()
        )
        item_name=args if args else None
        item=None
        if room_inventory and args:
            for each_item in room_inventory:
                if item_name in each_item.name:
                    item=each_item
                    break
            if item is not None:

                # Remove the item from Room_Inventory
                session.query(RoomInventory).filter(RoomInventory.object_id == item.id).delete()
                # Add the item to Mobile_Inventory
                session.add(MobileInventory(mobile_id=me.id, object_id=item.id))
                session.commit()  # Commit the changes to the database
                print(f'{str(me).capitalize()} picks up {item}.')
            else: 
                print(f'There is no {args} here.')
        elif not room_inventory: print('There is nothing here to get.')
        elif not args: print('Get what now?') 

    def drop(item_name=None, me:PlayerCharacter=None, **kwargs):
        ''' Drop <item> - Drop an item on the ground. '''

        if not item_name: # just.. DROP!  
            print("You drown down on one knee.")
            return False 
        
        item=None
        mobile_inventory = (
            session.query(Object)
            .join(MobileInventory, MobileInventory.object_id == Object.id)
            .filter(MobileInventory.mobile_id == me.id)
            .all())
        
        if item_name=="all":
          if mobile_inventory:  
            for each_item in mobile_inventory:
                CommandList.drop(item_name=each_item.name, me=me)                    
            return True
          else:
            print("You drop everything right away.")
            return False
            
        for each_item in mobile_inventory:
            if item_name in each_item.name: item = each_item

        if item is not None:
            session.query(MobileInventory).filter(MobileInventory.object_id == item.id).delete()
            session.add(RoomInventory(room_id=me.room_id, object_id=item.id))
            session.commit()
            print(f'You drop {item} on the ground.')
        else:     
            print(f"You don't have {item_name} in inventory.")

    def inventory(*args, me:PlayerCharacter=None, **kwargs):
        ''' Inventory - Check inventory. '''
        title=(f'  {str(me).capitalize()}\'s Inventory  ')
        print('-'*len(title))
        print(title)
        print('-'*len(title))
        inventory = (
            session.query(Object)
            .join(MobileInventory, MobileInventory.object_id == Object.id)
            .filter(MobileInventory.mobile_id == me.id)
            .all())
        if inventory: 
            for each_item in inventory:
                print(each_item)
        else: print('None')
        print()
        print('-'*len(title))
        title=(f'  {str(me).capitalize()}\'s Equipment  ')
        print(title)
        print('-'*len(title))
        print(f'Armor: {me.armor}')
        print(f'Weapon: {me.weapon}')
        return

    
    def equip(item_name, me:PlayerCharacter) -> bool:
        #TODO: ugh.. this is too much. We need a better command parser
        """Equips an item from the mobile's inventory.

        Args:
            item_name (str): Name of the item to equip (supports partial matching).
            me: The Mobile object equipping the item.     
        Returns:
            bool: True if the item was equipped successfully, False otherwise.
        """

        # Get the equippable item from inventory
        equipment=None
        for each_item in me.inventory:
            if item_name in each_item.name: equipment=each_item

        if equipment:
            # Check if there's an existing equipment for the specified type
            existing_equipment = session.query(MobileEquipment) \
                .filter(MobileEquipment.mobile_id == me.id) \
                .filter(MobileEquipment.type == equipment.type) \
                .first()

            # Handle existing equipment (replace/unequip/error)
            # ... (Implement your logic here based on game design)
          
            if existing_equipment: 
                print(f"You are already have an item of {equipment.type} equipped...")
                CommandList.unequip(session.query(Object.name).filter(Object.id == existing_equipment.object_id).first().name, me)

            # Add the item to Mobile_Equipment
            new_equip = MobileEquipment(mobile_id=me.id, type=equipment.type, object_id=equipment.id)
            session.add(new_equip)

            # Remove the item from MobileInventory (assuming one per type)
            session.query(MobileInventory).filter(
                MobileInventory.mobile_id == me.id, MobileInventory.object_id == equipment.id
            ).delete()

            session.commit()  # Commit the changes to the database
            print(f"{me.name} equips {equipment.name}.")
            return True
        else:
            print(f"You don't have any equipment that matches your request.")

        return False
                          
    def unequip(target_name:str, me: PlayerCharacter) -> bool:
        """Unequips an item from the mobile's equipment and puts it back into inventory."""
        if len(target_name) < 1: return False

        # 1. Get all equipped items:
        equipped_items = me.equipment
   
        # 1A. if "all"
        if target_name=="all":
            for item in equipped_items:
                CommandList.unequip(item.name, me)
            return True

        # 2. Find item containing word or substring:
        unequipped_item = None
        for equipped_item in equipped_items:
            if target_name.lower() in equipped_item.name.lower():
                unequipped_item = equipped_item
                break
        
        if not unequipped_item:
            print(f"You are not equipped with any item containing '{target_name}'.")
            return False

        # 3. Remove the item from MobileEquipment, add it to MobileInventory:
        new_unequip = new_unequip = session.query(MobileEquipment).filter(MobileEquipment.mobile_id == me.id, MobileEquipment.type == unequipped_item.type).first()
        session.delete(new_unequip)
        session.add(MobileInventory(mobile_id=me.id, object_id=unequipped_item.id))
        session.commit()

        print(f"You unequip {unequipped_item.name}.")
        return True

    def go(args, me:PlayerCharacter=None, **kwargs): #N,NE,E,SE,S,SW,W,NW,Up,Down,Out
        ''' Go <direction> - move into the next room in <direction>
     for cardinal directions you can just type the direction, eg:
     <north|east|south|west|[etc.]> or <N|NE|E|SE|S|SW|W|NW>'''
        if not args:
            print("Go where?")
            return False
        dir=args
        if dir=='n':dir='north'
        if dir=='ne':dir='northeast'
        if dir=='e':dir='east'
        if dir=='se': dir='southeast'
        if dir=='s':dir='south'
        if dir=='sw':dir='southwest'
        if dir=='w':dir='west'
        if dir=='nw':dir='northwest'
        for exit in me.room.exits:
            if exit.direction==dir: break
        else: 
            print(f"exit not found in direction '{dir}'")
            return False
        
        ### move player to the room in that direction ###
        from rooms import Exit, RoomMobiles
        print(f'{me.name.capitalize()} heads {dir}...')

        # Find the to_room_id from the Exits table
        to_room_id = session.query(Exit.to_room_id) \
                        .filter(Exit.from_room_id == me.room.id) \
                        .filter(Exit.direction == dir) \
                        .scalar()  # Retrieve a single value
      
        if to_room_id:  # Check weather a matching exit was found
            session.execute(
                update(RoomMobiles)  # Update the RoomMobiles table
                .where(RoomMobiles.mobile_id == me.id)  # Identify the mobile to update
                .values(room_id=to_room_id))  # Set the new room_id
            session.commit()  # Commit the changes to the database       
        
        else:
            print(f"Exit not found in {dir} direction.")

        rooms.look(me)

    def north(*args, me:PlayerCharacter=None, **kwargs):
        ''' alias for GO NORTH.'''
        CommandList.go('north', me=me)
    def northeast(*args, me:PlayerCharacter=None, **kwargs):
        ''' alias for GO NORTHEAST.'''
        CommandList.go('northeast', me=me)
    def east(*args, me:PlayerCharacter=None, **kwargs):
        ''' alias for GO EAST.'''
        CommandList.go('east', me=me)
    def southeast(*args, me:PlayerCharacter=None, **kwargs):
        ''' alias for GO SOUTHEAST.'''
        CommandList.go('southeast', me=me)
    def south(*args, me:PlayerCharacter=None, **kwargs):
        ''' alias for GO SOUTH.'''
        CommandList.go('south', me=me)
    def southwest(*args, me:PlayerCharacter=None, **kwargs):
        ''' alias for GO SOUTHWEST.'''
        CommandList.go('southwest', me=me)
    def west(*args, me:PlayerCharacter=None, **kwargs):
        ''' alias for GO WEST.'''
        CommandList.go('west', me=me)
    def northwest(*args, me:PlayerCharacter=None, **kwargs):
        ''' alias for GO NORTHWEST'''
        CommandList.go('northwest', me=me)
    def up(*args, me:PlayerCharacter=None, **kwargs):
        ''' alias for GO UP.'''
        CommandList.go('up', me=me)
    def down(*args, me:PlayerCharacter=None, **kwargs):
        ''' alias for GO DOWN.'''
        CommandList.go('down', me=me)
    
    
        
    # abbreviations and shortcuts:
    inv=inventory
    d=down
    n=north
    ne=northeast
    e=east
    se=southeast
    s=south
    sw=southwest
    w=west
    nw=northwest
    l=look
    q=quit

    def fight(args, me=None, **kwargs):
        ''' Fight <target> - Initiate combat.'''
        debug("initiating fight...")
        debug(f"me={me.__repr__()} - ({me.name})")
        targets=me.room.mobiles
        debug(f"possible targets:{targets}")
        mob_name=args if args else None
        debug(f"mob_name = {mob_name}")
        if mob_name==None:return 0
        mob=None
        if targets and args:
            debug(f"for target in targets:")
            for target in targets:
                debug(f"target: {target}")
                debug(f"if mob_name in target.name:")
                debug(f"if {mob_name} in {target.name}:")
                if mob_name in target.name:
                    mob=target
                    break
            if mob is not None:
                print(f'{str(me).capitalize()} lunges at {mob}.')
                import combat
                combat.attack(me, mob)
            else: 
                print(f'There is no {args} here.')
        elif not target: print('There is nobody here to fight.')
        elif not args: print('Fight who now?') 


def parse(myself : PlayerCharacter, user_input : str) -> bool:
    if user_input:
        
        command, *args = user_input.split()    
        target_name = " ".join(args)
        
        action = getattr(CommandList, command, None)
        if action: 
            action(target_name, me=myself) if target_name else action(me=myself)
        else: print(f'Unknown command "{command}".')
    else: print('Huh?')