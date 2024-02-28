import queue
from main import PROMPT
from objects import Object
from mobiles import Mobile, MobileInventory, MobileEquipment
from typing import Union
from rooms import Room, RoomInventory
from dungeon_data import session

DEBUG=False
def debug(message): print(f'{__name__} *** DEBUG *** {message}') if DEBUG else None
debug(f'{DEBUG}')

action_queue=queue.Queue()
Any = Union[Mobile, Object, None]

class Action(): 
    """
    format:
        def action(self:Mobile=None, arg:str=None, target:Any=None):

    class for game engine actions. This is not to be accessed directly.
    instead, use:
        do(self, action, arg, target)
    """
    def say(self:Mobile=None, arg:str=None, **kwargs):
        print(f'{self} says "{arg}"')
    
    def announce(self:Mobile=None, arg:str=None, **kwargs):
        """
        announce to the room. This will be useful when multi-player is added.
        """
        print(f"{arg}")

    def get(self:Mobile, target:Object, **kwargs):
        # Remove the item from Room_Inventory
        session.query(RoomInventory).filter(RoomInventory.object_id == target.id).delete()
        # Add the item to Mobile_Inventory
        session.add(MobileInventory(mobile_id=self.id, object_id=target.id))
        session.commit()  # Commit the changes to the database
        print(f'You pick up {target}.')

    def drop(self:Mobile, target:Object, **kwargs):
        if not target: # just.. DROP!  
            print("You drop down on one knee.")
            return 
        session.query(MobileInventory).filter(MobileInventory.object_id == target.id).delete()
        session.add(RoomInventory(room_id=self.room.id, object_id=target.id))
        session.commit()
        print(f'You drop {target}.')

    def equip(self:Mobile, target:Object, **kwargs):
        # Add the item to Mobile_Equipment
        new_equip = MobileEquipment(mobile_id=self.id, type=target.type, object_id=target.id)
        session.add(new_equip)

        # Remove the item from MobileInventory 
        session.query(MobileInventory).filter(
            MobileInventory.mobile_id == self.id, MobileInventory.object_id == target.id
        ).delete()

        session.commit()  # Commit the changes to the database
        print(f"You equip {target.name}.")    
        
    def unequip(self:Mobile, target:Object, **kwargs):
        new_unequip = session.query(MobileEquipment).filter(MobileEquipment.mobile_id == 
                      self.id, MobileEquipment.type == target.type).first()
        session.delete(new_unequip)

        session.add(MobileInventory(mobile_id=self.id, object_id=target.id))
        session.commit()

        print(f"You unequip {target.name}.")

    def fight(self:Mobile=None, arg:str=None, target:Any=None):
            print(f'{str(self).capitalize()} lunges at {target}.')
            from combat import Combat
            Combat(self, target)

    def go(self:Mobile, arg:str, **kwargs):
        # TODO: get action from CommandList (cut/paste)
        pass

def do(self:Mobile=None, action:str=None, arg:str=None, target:Any=None):
    debug(f"do(SAAT): {self}, {action}, {arg}, {target}")
    # check Action class for action:
    do_action=getattr(Action, action, None)
    if do_action: do_action(self=self, arg=arg, target=target)
    else:
        print(f"*** BUG ***: action '{action}' not found:\n    {do_action}\n")

def add_to_queue(self=None, action=None, arg=None, target=None, **kwargs):   
    debug(f"SAAT2Q: {(self, action, arg, target)}'")
    action_queue.put((self, action, arg, target))

def update_game():
    if not action_queue.empty(): 
        print()
        while not action_queue.empty():
            self, action, arg, target = action_queue.get(block=False)  # Non-blocking get
            do(self, action, arg, target)
        print(PROMPT)
        
