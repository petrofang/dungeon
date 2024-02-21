#commands.py
from dungeon_data import session, joinedload
import rooms, objects, mobiles
from players import PlayerCharacter
from mobiles import MobileInventory, MobileEquipment, Mobile
from objects import Object, ItemTypes

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

    def look(*args, me:PlayerCharacter=None, **kwargs):
        ''' Look - take a look at the place you are in. '''
        rooms.look(me.room_id)

    def get(*args, me:PlayerCharacter=None, **kwargs):
        ''' Get <item> - Get an item from the room. '''
        # TODO: "get all"
         # Join Room_Inventory with Objects to get Object instances
        room_inventory = (
            session.query(objects.Object)
            .join(rooms.RoomInventory, rooms.RoomInventory.object_id == objects.Object.id)
            .filter(rooms.RoomInventory.room_id == me.room_id)
            .all()
        )
        item_name=args[-1] if args else None
        item=None
        if room_inventory and args:
            for each_item in room_inventory:
                if item_name in each_item.name:
                    item=each_item
                    break
            if item is not None:

                # Remove the item from Room_Inventory
                session.query(rooms.RoomInventory).filter(rooms.RoomInventory.object_id == item.id).delete()
                # Add the item to Mobile_Inventory
                session.add(mobiles.MobileInventory(mobile_id=me.id, object_id=item.id))
                session.commit()  # Commit the changes to the database
                print(f'{str(me).capitalize()} picks up {item}.')
            else: 
                print(f'There is no {args[-1]} here.')
        elif not room_inventory: print('There is nothing here to get.')
        elif not args: print('Get what now?') 

    def drop(*args, me:PlayerCharacter=None, **kwargs):
        ''' Drop <item> - Drop an item on the ground. '''
        # TODO: "drop all"
        if not args: 
            print('Drop what now?')
            return
        item=None
         # Join Mobile_Inventory with Objects to get Object instances
        mobile_inventory = (
            session.query(objects.Object)
            .join(mobiles.MobileInventory, mobiles.MobileInventory.object_id == objects.Object.id)
            .filter(mobiles.MobileInventory.mobile_id == me.id)
            .all())
        
        for each_item in mobile_inventory:
            if args[-1] in each_item.name:
                item = each_item
        if item is not None:
            session.query(mobiles.MobileInventory).filter(mobiles.MobileInventory.object_id == item.id).delete()
            session.add(rooms.RoomInventory(room_id=me.room_id, object_id=item.id))
            session.commit()
            print(f'{str(me).capitalize()} drops {item} on the ground.')
        else:     
            print(f"{str(me).capitalize()} doesn't have {args[-1]} in inventory.")

    def inventory(*args, me:PlayerCharacter=None, **kwargs):
        ''' Inventory - Check inventory. '''
        title=(f'  {str(me).capitalize()}\'s Inventory  ')
        print(title)
        print('-'*len(title))
        inventory = (
            session.query(objects.Object)
            .join(mobiles.MobileInventory, mobiles.MobileInventory.object_id == objects.Object.id)
            .filter(mobiles.MobileInventory.mobile_id == me.id)
            .all())
        if inventory: 
            for each_item in inventory:
                print(each_item)
        else: print('None')

        title=(f'  {str(me).capitalize()}\'s Equipment  ')
        print(title)
        print('-'*len(title))
        print(f'Armor: {me.armor}')
        print(f'Weapon: {me.weapon}')
        return

    
    def equip(*args, me:PlayerCharacter) -> bool:
        #TODO: ugh.. this is too much. We need a better command parser
        """Equips an item from the mobile's inventory.

        Args:
            item_name (str): Name of the item to equip (supports partial matching).
            me: The Mobile object equipping the item.     
        Returns:
            bool: True if the item was equipped successfully, False otherwise.
        """
        # Convert input to lowercase for case-insensitive comparison
        item_name = args[-1]        
        user_input = item_name.lower()

        # Get the equippable item from inventory
        item = session.query(Object) \
            .join(MobileInventory, MobileInventory.object_id == Object.id) \
            .filter(MobileInventory.mobile_id == me.id) \
            .filter(Object.name.like(f"%{user_input}%")) \
            .filter(Object.type.in_(session.query(ItemTypes.name).filter(ItemTypes.is_equipable == True))) \
            .first()

        if item:
            # Check if there's an existing equipment for the specified type
            existing_equipment = session.query(MobileEquipment) \
                .filter(MobileEquipment.mobile_id == me.id) \
                .filter(MobileEquipment.type == item.type) \
                .first()

            # Handle existing equipment (replace/unequip/error)
            # ... (Implement your logic here based on game design)
          
            if existing_equipment: 
                print(f"You already wear {existing_equipment}")
                return False

            # Add the item to Mobile_Equipment
            new_equip = MobileEquipment(mobile_id=me.id, type=item.type, item_id=item.id)
            session.add(new_equip)

            # Remove the item from MobileInventory (assuming one per type)
            session.query(MobileInventory).filter(
                MobileInventory.mobile_id == me.id, MobileInventory.object_id == item.id
            ).delete()

            session.commit()  # Commit the changes to the database
            print(f"{me.name} equips {item.name}.")
            return True
        else:
            print(f"You don't have any armor that matches your request.")

        return False
                          
    def unequip(*args, me: PlayerCharacter) -> bool:
        """Unequips an item from the mobile's equipment and puts it back into inventory."""

        item_name = args[-1].lower() # janky, just uses the last word in the command as the item name

        # 1. Get all equipped items:
        equipped_items = session.query(MobileEquipment) \
            .options(joinedload('item_type'))           \
            .filter(MobileEquipment.mobile_id == me.id) \
            .filter(MobileEquipment.item.type.in_(
                session.query(ItemTypes.name).filter(ItemTypes.is_equipable == True)
            )) \
            .all()

        # 2. Find item containing word or substring:
        unequipped_item = None
        for equipped_item in equipped_items:
            if item_name in equipped_item.item.name.lower():
                unequipped_item = equipped_item
                break
        
        if not unequipped_item:
            print(f"You are not equipped with any item containing '{item_name}'.")
            return False

        # 3. Remove the item from MobileEquipment, add it to MobileInventory:
        session.delete(unequipped_item)
        session.add(MobileInventory(mobile_id=me.id, object_id=unequipped_item.item_id))
        session.commit()
        print(f"{me.name} unequips {unequipped_item.item.name}.")
        return True



#################### TODO: EVERYTHING BELOW THIS LINE STILL NEEDS TO BE CHECKED AND UPDATED



    def fight(*args, me=None, **kwargs):
        ''' Fight <target> - Initiate combat.'''
        room=me.room.mobiles
        mob_name=args[-1] if args else None
        mob=None
        if room and args:
            for each in room.values():
                if mob_name in each.name and each.dead==False:
                    mob=each
                    break
            if mob is not None:
                from combat import fight
                print(f'{str(me).capitalize()} lunges at {mob}.')
                fight(me, mob)
            else: 
                print(f'There is no {args[-1]} here.')
        elif not room: print('There is nobody here to fight.')
        elif not args: print('Fight who now?') 

    def go(*args, me:PlayerCharacter=None, **kwargs): #N,NE,E,SE,S,SW,W,NW,Up,Down,Out
        ''' Go <direction> - move into the next room in <direction>
     for cardinal directions you can just type the direction, eg:
     <north|east|south|west|[etc.]> or <N|NE|E|SE|S|SW|W|NW>'''
        dir=args[0]
        if dir=='n':dir='north'
        if dir=='ne':dir='northeast'
        if dir=='e':dir='east'
        if dir=='se': dir='southeast'
        if dir=='s':dir='south'
        if dir=='sw':dir='southwest'
        if dir=='w':dir='west'
        if dir=='nw':dir='northwest'
        if dir in me.room.exits:
            # move player to the room in that direction
            print(f'{me.name.capitalize()} heads {dir}.')
            me.room=me.room.exits[dir]
            me.room.look()

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
    
    
        
    # abbreviations and shortcuts:
    inv=inventory
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

def main():
    from main import PROMPT
    me=PlayerCharacter()
    CommandList.help()
    while True:
        user_input = input(PROMPT).lower()
        if user_input:
            command, *args = user_input.split()
            command = getattr(CommandList, command, None)
            if command: 
                command(*args, me=me) if args else command(me=me)
            else: print(f'Unknown command "{user_input}".')
        else: print('Huh?')


if __name__ == '__main__': main()