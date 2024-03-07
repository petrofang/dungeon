from dungeon_data import Base, Boolean, Column, Integer, JSON
from dungeon_data import ForeignKey, String, relationship, session
from objects import Object

cardinals=['north', 'northeast', 'east', 'southeast', 'south', 'southwest', 
           'west', 'northwest', 'up', 'down', 'out']
        
class Exit(Base):
    """
    Exit defines an exit from one room to another. Each exit is one-way,
    so another exit object must describe the return exit, if there is one.

    attributes:
        from_room_id, to_room_id - the Room.id of the respective rooms.
        direction - can be any of the cardinal directions, down, up, or out.
            it can also be a keyword describing the exit, eg "door", "gate".
            it may also describe a building entrance, eg "inn", "house".
        description - A description of the exit, what the player will see
            when they look at it. If entrance=true, it should describe what
            the entrance is to, eg the outside of the inn. If no description
            is set, a brief view will be generated by the Exit.look()
        entrance - if the keyword describes the thing being entered, rather
            than the exit itself. This is necessary to avoid things like
            "Player goes house," or "Player goes through the house," which
            both have unintended meanings from "Player enters the house". 
        door - if the exit can be opened and closed. 
        is_open - if the door is open (False if closed)
        has_lock - if it is lockable
        is_locked - if it is currently locked
        hidden - if the exit is hidden (not listen in room's exits)
    """
    __tablename__ = "exits"

    from_room_id = Column(Integer, ForeignKey("rooms.id"), primary_key=True)
    to_room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    direction = Column(String(32), primary_key=True)
    description = Column(String(65535))
    entrance = Column(Boolean, nullable=False) 
    is_door = Column(Boolean, nullable=False)
    is_open = Column(Boolean, nullable=False)
    has_lock = Column(Boolean, nullable=False)
    is_locked = Column(Boolean, nullable=False)
    hidden = Column(Boolean, nullable=False)
    # TODO - keys.. how to make non-unique key object? JSON

    @property
    def backref(self):
        back_exit=None
        for exit in self.to_room.exits:
            if exit.to_room == self.from_room:
                back_exit = exit
        return back_exit
        
    @property
    def to_room(self):
        return session.query(Room).filter(Room.id==self.to_room_id).first()
    
    @property
    def from_room(self):
        return session.query(Room).filter(Room.id==self.from_room_id).first()

    def unlock(self):
        # TODO: make an actions.Action.unlock() method
        # TODO: check for key in actions.Action.unlock()
        self.is_locked=False

    def lock(self):
        # TODO: make an actions.Action.lock() method
        # TODO: check for key in actions.Action.lock()
        if self.has_lock: self.is_locked=True

    def open(self): # TODO: handle echoing in actions.Action.open_door()
                    self.is_open=True
                    self.backref.is_open=True
                    session.commit()

    def close(self): 
                self.is_open=False
                self.backref.is_open=False
                session.commit()

    @property
    def way(self):
        way = "entrance to the " if self.entrance else ""
        way = "way " if self.direction in cardinals else way   
        return way

    def look(self, viewer):
        """
        Displays description of an exit, 
        and the name of the next room (if exit is open)
        """           
        if self.description == None:  # there's no description set
            if not self.is_open:       # and it's closed
                viewer.print(f"The {self.way}{self.direction} is closed.")
            else:                   # and it's open
                viewer.print(f"The {self.way}{self.direction}",
                      f"leads to {self.to_room.name}.")
        else:                     # there is a desciption set   
            closed = "(closed)" if not self.is_open else ""
            viewer.print(f"[ {self.direction} ]: {closed}\n  {self.description}")


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255), nullable=False)   
    signs = Column(JSON)
    commands = Column(JSON)
    """
    JSON format of Room.commands is as follows:
    {
        "perform action":{
            "action": "action_name" # method in actions.Action,
            "echo": "message to echo to the room"
            "arg": "argument to be passed to actions.do",
            "target": "target to be passed to actions.do"
        }
    }
    """

    def command(self, subject, command=None):
        import actions
        if command and self.commands:
            if self.commands[command]:
                command=self.commands[command]
                action = command.get("action")
                arg = command.get("arg")
                target = command.get("target")
                echo = command.get("echo")
            if echo: 
                actions.echo(subject, echo)
            if action:
                actions.do(subject, action, arg, target)

    @property
    def exits(self):
        """List of exits or None."""
        exits=session.query(Exit).filter(Exit.from_room_id == self.id).all()
        return exits

    def exit(self, direction:str=None):
        """ 
        Room.exit(direction)

        returns the Exit object of the exit in direction, or None
        """
        if direction==None: return None
        for exit in self.exits:
            if exit.direction==direction:
                return exit
        else: return None

    @property
    def inventory(self):

        objects = session.query(Object).join(RoomInventory, 
            RoomInventory.object_id == Object.id).filter(
            RoomInventory.room_id == self.id).all()

        return objects if objects else []

    @property
    def mobiles(self):
        """
        Room.mobiles - list of all mobiles in the room
        """
        from mobiles import Mobile
        mobiles = session.query(Mobile).join(RoomMobiles, 
            RoomMobiles.mobile_id == Mobile.id).filter(
            RoomMobiles.room_id == self.id).all()

        return mobiles if mobiles else []
    
    @property
    def players(self):
        """
        Room.players - list of all players in the room
        """
        players = []
        from players import PlayerCharacter
        for mobile in self.mobiles:
            player = session.query(PlayerCharacter).filter(
                PlayerCharacter.id == mobile.id).first()
            if player: players.append(player)
        return players
    
    def remove(self, target=None):
        """
        Remove target Object or Mobile from the room. 
        """
        from mobiles import Mobile
        if isinstance(target, Object):
            if target in self.inventory:
                session.delete(session.query(RoomInventory).filter(
                RoomInventory.object_id == target.id).first())
        elif isinstance(target, Mobile):
            if target in self.mobiles:
                session.delete(session.query(RoomMobiles).filter(
                    RoomMobiles.mobile_id == target.id).first())
        session.commit()

    def add(self, target):
        """
        add target Object or Mobile to the room
        """
        from mobiles import Mobile
        if isinstance(target, Mobile): RoomMobiles(self, target.id)
        elif isinstance(target, Object): RoomInventory(self, target.id)
        session.commit()


    def look(self, viewer, sign=None, **kwargs):
        """
        Displays the title, description, items, mobiles, exits of given room.

        Args:
            viewer - The player who is the doing the looking.
            sign - a 'sign' or extra description within the room.
        """
        
        if sign:
            if self.signs and sign in self.signs.keys(): 
                viewer.print(self.signs[sign])
        else:
            viewer.print(f"[ {self.name} ] ({self.id})")
            viewer.print(f"  {self.description}", end='')

            if self.inventory:
                if len(self.inventory) == 1:
                    viewer.print(f" A solitary {self.inventory[0].name} rests here.")
                else:
                    viewer.print(" Scattered about, you see a", end="")
                    for i, obj in enumerate(self.inventory[:-1]):
                        viewer.print(f" {obj.name}", end=",")
                    viewer.print(f" and a {self.inventory[-1].name}.")
            

            # List mobiles; filter out the player character
            other_mobiles = [mobile for mobile in self.mobiles 
                            if mobile.id != viewer.id]
            other_mobiles_names = []
            for mobile in other_mobiles:
                if mobile.type == "player" or mobile.type == "NPC":
                    other_mobiles_names.append(mobile.name)
                else:
                    other_mobiles_names.append(f"a {mobile.name}")
            if other_mobiles_names:
                viewer.print(" Sharing the space with you ", end="")

                # Handle edge case: single mobile
                if len(other_mobiles_names) == 1:
                    viewer.print(f"is {other_mobiles_names[0]}.")

                else:
                    viewer.print("are", end="")
                    for mob in other_mobiles_names[:-1]:
                        viewer.print(f" {mob}", end=",")
                    viewer.print(f" and {other_mobiles_names[-1]}.")
            
            if not other_mobiles_names and not self.inventory:
                viewer.print()

            viewer.print("  Obvious exits:\n[ ", end="")
            # list of non-hidden exits. 
            #   cardinal directions added first, 
            #   then keyword exits
            obvious_exits = [exit.direction for exit in self.exits 
                            if exit.direction in cardinals 
                            and exit.hidden==False]
            obvious_exits.extend([exit.direction for exit in self.exits 
                                if exit.direction not in cardinals 
                                and exit.hidden==False])
            if not obvious_exits: 
                viewer.print('None')
            else:
                obvious_exits=", ".join(obvious_exits)
                viewer.print(obvious_exits, end="")
            viewer.print(" ]")


class RoomInventory(Base):
    __tablename__ = "room_inventory"

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)  
    object_id = Column(Integer, ForeignKey("objects.id"), nullable=False)
    room = relationship("Room")
    object = relationship("Object")

    def __init__(self, room_id, object_id):
        self.room_id=room_id
        self.object_id=object_id


class RoomMobiles(Base):
    from mobiles import Mobile
    __tablename__="room_mobiles"

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)  
    mobile_id = Column(Integer, ForeignKey("mobiles.id"), nullable=False)  
    room = relationship("Room")
    mobile = relationship("Mobile")

    def __init__(self, room_id, mobile_id):
        self.room_id=room_id
        self.mobile_id=mobile_id
