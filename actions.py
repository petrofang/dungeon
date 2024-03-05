import queue, time
from main import PROMPT
from objects import Object
from mobiles import Mobile, MobilePrototype, MobileInventory, MobileEquipment
from typing import Union
from rooms import Exit, RoomInventory, cardinals
from dungeon_data import session

action_queue=queue.Queue()

class Action(): 
    """
    This is the class for game engine actions. This is not to be 
    accessed directly. instead, use: 
        do(self, action, arg, target)

    commands.parse() and commands.CommandList handle player input,
    before sending SAAT (Subject, Action, Arguments, Target) to be
    directed by the do() function and ultimately this the Action 
    class. 

    Generally, any command which causes changes to the game state
    or any interaction with any game object, mobile or player should
    pass through this class.

    format:
        def action(self:Mobile, arg:str, target, **kwargs):
    """
    # TODO: better error and exception handling throughout

    def say(self:Mobile, arg:str, target=None):
        print(f'{self} says "{arg}"')
    
    def emote(self:Mobile, arg:str, target=None):
        print(f"You {arg}.")

    def spawn(self, arg, **kwargs):
        # arg = ID of the Mobile Prototype you'd like to spawn
        prototype=session.query(MobilePrototype).filter(
            MobilePrototype.id==arg).first()
        prototype.spawn(invoker=self)

    def echo(self:Mobile=None, arg:str=None, **kwargs):
        print(f"{arg}")

    def get(self:Mobile, target:Object, arg:Object=None, **kwargs):
        # Remove the item from room and add to inventory
        if arg and target:
            # if a container (arg) and item (target) are supplied
            print(f"You get a {target} from the {arg}.")
            arg.get(target)
            self.add_to_inventory(target)
        elif target:
            print(f'You pick up {target}.')
            self.room.remove(target)
            self.add_to_inventory(target)

    def put(self:Mobile, target:Object, arg:Object=None, **kwargs):
        print(f"You put a {target} in the {arg}.")
        arg.put(target)
        self.remove_from_inventory(target)

    def drop(self:Mobile, target:Object, **kwargs):
        # remove item from inventory and add to room
        session.query(MobileInventory).filter(
            MobileInventory.object_id == target.id
            ).delete()
        session.add(RoomInventory(
            room_id=self.room.id, 
            object_id=target.id))
        session.commit()
        print(f'You drop {target}.')

    def equip(self:Mobile, target:Object=None, **kwargs):
        # Add the item to Mobile_Equipment
        if target:
            if self.equipment[target.type] == None:
                if target in self.inventory:
                    self.remove_from_inventory(target)
                    self.equip(target)
                    print(f"You equip {target.name}.")    
            
    def unequip(self:Mobile, target:Object=None, **kwargs):
        if target:
            if target in self.equipment.values():
                self.unequip(target)
                self.add_to_inventory(target)
                print(f"You unequip {target.name}.")

    def fight(self:Mobile, arg:str, target:Mobile):
            print(f'{str(self).capitalize()} lunges at {target}...')
            from combat import Combat
            Combat(self, target)

    def go(self:Mobile, arg:str, **kwargs):
        if self.room.exit(arg).is_open:
            if arg in cardinals:
                print(f'You go {arg}...')
            else:
                print(f'You go through the {arg}...')
            time.sleep(.5)
            self.goto(self.room.exit(arg).to_room.id)
            self.room.look(self)
        else: 
            if arg in cardinals:
                print(f"The way {arg} is closed.")
            else:
                print(f"The {arg} is closed.")
    
    def open_door(self:Mobile, arg:str, target:Exit):
        target.open()

    def close_door(self:Mobile, arg:str, target:Exit):
        target.close()

def do(self:Mobile = None, action:str = None, arg:str = None, target=None):
    # check Action class for action:
    do_action=getattr(Action, action, None)
    if do_action: do_action(self=self, arg=arg, target=target)
    else:
        print(f"* BUG *: action '{action}' not implemented.")
        raise NotImplementedError

def add_to_queue(self=None, action=None, arg=None, target=None, **kwargs):   
    action_queue.put((self, action, arg, target))

def update_game():
    if not action_queue.empty(): 
        print()
        while not action_queue.empty():
            self, action, arg, target = action_queue.get(block=False) 
            do(self, action, arg, target)
        print(PROMPT)
        
