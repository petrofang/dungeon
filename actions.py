import queue, time
from objects import Object
from mobiles import Mobile, MobilePrototype
from rooms import Exit, cardinals
from dungeon_data import session

action_queue=queue.Queue()

class Action(): 
    """
    This is the class for game engine actions. This is not to be 
    accessed directly. instead, use: 
        do(subject, action, arg, target)

    commands.parse() and commands.CommandList handle player input,
    before sending SAAT (Subject, Action, Arguments, Target) to be
    directed by the do() function and ultimately this the Action 
    class. 

    Generally, any command which causes changes to the game state
    or any interaction with any game object, mobile or player should
    pass through this class.

    format:
        def action(subject:Mobile, arg:str, target, **kwargs):
    """
    # TODO: better error and exception handling throughout
    # TODO: consistant method parameters (positional, not keyword?)
    #       (get rid of **kwargs)

    def say(subject:Mobile, arg:str, target=None):
        echo_around(subject, f'{subject} says "{arg}"')
        echo_at(subject, f'You say, "{arg}"')
    
    def emote(subject:Mobile, arg:str, target=None):
        emote = arg
        if emote:
            if emote[-1] not in ";,'.!?\"":
                emote = emote + "."
            echo(subject, f"{subject} {emote}")

    def spawn(subject, arg=1, target=None):
        # subject = person spawning (location to spawn)
        # target = ID of the Mobile Prototype you'd like to spawn
        # arg = max instances of spawned mobile in the room
        prototype = session.query(MobilePrototype).filter(
            MobilePrototype.id==target).first()
        max_mobs = arg 
        mob_count = 0
        for mobile in subject.room.mobiles:
            if mobile.prototype_id == arg:
                mob_count += 1
        if mob_count < max_mobs:
            prototype.spawn(invoker=subject) if prototype else None

    # TODO: check the positional argument here:
    def get(subject:Mobile, target:Object, arg:Object=None, **kwargs):
        # Remove the item from room or container and add to inventory
        item, container = target, arg
        if arg and target:
            # if a container (arg) and item (target) are supplied
            echo_at(subject, f"You get a {item} from the {container}.")
            echo_around(subject, f"{subject} gets {item} from {container}.")
            container.get(item)
            subject.add_to_inventory(item)
        elif item:
            echo_at(subject, f'You pick up {item}.')
            echo_around(subject, f'{subject} picks up {item}.')
            subject.room.remove(item)
            subject.add_to_inventory(item)

    def put(subject:Mobile, target:Object, arg:Object=None, **kwargs):
        echo_at(subject, f"You put a {target} in the {arg}.")
        echo_around(subject, f"{subject} puts {target} in the {arg}.")
        arg.put(target)
        subject.remove_from_inventory(target)

    def drop(subject:Mobile, target:Object, **kwargs):
        # remove item from inventory and add to room
        subject.remove_from_inventory(target)
        subject.room.add(target)
        session.commit()
        echo_at(subject, f'You drop {target}.')
        echo_around(subject, f"{subject} drop {target}.")

    def equip(subject:Mobile, target:Object=None, **kwargs):
        # Add the item to Mobile_Equipment
        if target:
            if subject.equipment[target.type] == None:
                if target in subject.inventory:
                    subject.remove_from_inventory(target)
                    subject.equip(target)
                    echo_at(subject, f"You equip {target.name}.")    
                    echo_around(subject, f"{subject} equips {target.name}.")

    def unequip(subject:Mobile, target:Object=None, **kwargs):
        if target:
            if target in subject.equipment.values():
                subject.unequip(target)
                subject.add_to_inventory(target)
                echo_at(subject, f"You unequip {target.name}.")    
                echo_around(subject, f"{subject} unequips {target.name}.")

    def fight(subject:Mobile, arg:str, target:Mobile):
            echo_at(subject, f'You lunge at {target}...')
            echo_around(subject, f'{subject} lunges at {target}...')
            from combat import Combat
            Combat(subject, target)

    def transfer(subject, arg, target:int):
        # transfer the player/mobile directly to the target room
        room_id = target
        subject.goto(room_id)


    def go(subject:Mobile, arg:str, **kwargs):
        exit = subject.room.exit(arg) 
        if exit.is_open:
            if exit.direction in cardinals:
                if not exit.climb:        
                    echo_at(subject, f'You go {exit.direction}...')
                    echo_around(subject, f'{subject} goes {exit.direction}.')
                else:
                    echo_at(subject, f'You climb {exit.direction}...')
                    echo_around(subject, f'{subject} climbs {exit.direction}.')
            elif exit.entrance:
                if not exit.climb:    
                    echo_at(subject, f'You enter the {exit.direction}...')
                    echo_around(subject, f'{subject} enters the {exit.direction}.')
                else:
                    echo_at(subject, f'You climb into the {exit.direction}...')
                    echo_around(subject, f'{subject} climbs into the {exit.direction}.')
            else:
                if not exit.climb:
                    echo_at(subject, f'You go through the {exit.direction}...')
                    echo_around(subject, f'{subject} goes through the {exit.direction}.')
                else:
                    echo_at(subject, f'You climb the {exit.direction}...')
                    echo_around(subject, f'{subject} climbs the {exit.direction}.')
            time.sleep(.5)
            subject.goto(exit.to_room_id)
            if exit.backref:
                echo_around(subject, f"{subject} arrives from the {exit.backref.direction}.")
            else:
                echo_around(subject, f'{subject} arrives.')
            subject.room.look(subject)
        else: 
            if exit.direction in cardinals:
                echo_at(subject, f"The way {exit.direction} is closed.")
            elif exit.entrance:
                echo_at(subject, f"The entrance to the {exit.direction} is closed.")
            else:
                echo_at(subject, f"The {exit.direction} is closed.")
    
    def open_door(subject:Mobile, arg:str, target:Exit):
        target.open()

    def close_door(subject:Mobile, arg:str, target:Exit):
        target.close()
    

def do(subject:Mobile = None, action:str = None, arg:str = None, target=None):
    # TODO: remove default arguments to these parameters
    # TODO: but first, check all commands.CommandList methods
    #           to make sure they call this function with positional arguments
    do_action=getattr(Action, action, None)
    if do_action: do_action(subject=subject, arg=arg, target=target)
    else:
        print(f"* BUG *: action '{action}' not implemented.")
        raise NotImplementedError

def add_to_queue(subject=None, action=None, arg=None, target=None, **kwargs):  
    """ add an action to the action queue to be performed at the next tick"""
    action_queue.put((subject, action, arg, target))

def update_game():
    if not action_queue.empty(): 
        print()
        while not action_queue.empty():
            subject, action, arg, target = action_queue.get(block=False) 
            do(subject, action, arg, target)

def echo_at(player, message:str = "", end="\n"):
    """
    echo a message to player.
    """
    player.print(message, end)

def echo_around(player, message:str = "", end="\n"):
    """
    echo a message to others in player's room.
    """
    if player.room.players:
        for other in player.room.players:
            if other.id != player.id:
                echo_at(other, message, end)
    
def echo(player, message:str = "", end="\n"):
    """
    echo a message to all players in player's room.
    """
    if player.room.players:
        for each in player.room.players:
            echo_at(each, message, end)

def echo_global(message:str = "", end="\n"):
    """
    echo a message to all players.
    """
    import players
    for id in players.player_sockets.keys():
        player = players.get_player_by_id(id)
        echo_at(player, message, end)
