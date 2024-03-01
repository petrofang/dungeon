#rooms.py

DEBUG=True
def debug(message): print(f'{__name__} *** DEBUG *** {message}') if DEBUG else None
debug(f'{DEBUG}')

from dungeon_data import Base, Boolean, Column, Integer, ForeignKey, String, relationship, Session, session
from objects import Object

cardinals=['north', 'northeast', 'east', 'southeast', 'south', 'southwest', 'west', 'northwest', 'up', 'down', 'out']
        
class Exit(Base):
    __tablename__ = "Exits"

    from_room_id = Column(Integer, ForeignKey("Rooms.id"), primary_key=True)
    to_room_id = Column(Integer, ForeignKey("Rooms.id"), nullable=False)
    direction = Column(String(32), primary_key=True)
    description = Column(String(65535))
    door=Column(Boolean)
    is_open=Column(Boolean)
    hidden=Column(Boolean)
    is_locked=Column(Boolean)
    # TODO - lock, unlock functions, keys.... how to make non-unique key object?

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

    def open(self): # TODO: handle error checking with CommandList.close()
                    # and the echoing should be handled by actions.Action 
        way = "way leading " if self.direction in cardinals else ""                
        # is it a door?
        if self.door:
            # is it closed?
            if not self.is_open:
                # is it not locked?
                if not self.is_locked:
                    self.is_open=True
                    self.backref.is_open=True
                    session.commit()
                    # is it a cardinal direction or a keyword?
                    print(f"You open the {way}{self.direction}.")
                # is it locked?
                else:
                    print("You try to open it, but it is locked.")
            # is it open?
            else:
                print(f"The {way}{self.direction} is already open.")
        # is it not a door?
        else:
            print(f"The {way}{self.direction} cannot be opened nor closed.")

    def close(self): # TODO: handle error checking with CommandList.close()
                     # and the echoing should be handled by actions.Action
        way = "way leading " if self.direction in cardinals else "" 
        # is it a door?
        if self.door:
            # is it open?
            if self.is_open:
                self.is_open=False
                self.backref.is_open=False
                print(f"You close the {way}{self.direction}.")
            # is it closed?
            else:
                print(f"The {way}{self.direction} is already closed.")
        # is it not a door?
        else: 
            print(f"The {way}{self.direction} cannot be closed nor opened.")

    def look(self, **kwargs):
        """
        Displays description of an exit, 
        and the name of the next room (if exit is open)
        """
        
        cardinals=['north', 'northeast', 'east', 'southeast', 'south', 'southwest', 'west', 'northwest', 'up', 'down', 'out']
        if self.description == None:  # there's no description set
            if not self.is_open:       # and it's closed
                if self.direction in cardinals: # and it's a direction
                    print(f"The way {self.direction} is closed.")
                else:                           # it's a keyword
                    print(f"The {self.direction} is closed.")
            else:                   # and it's open
                if self.direction in cardinals: # and it's a direction
                    print(f"The way {self.direction} leads to {self.to_room.name}.")
                else:               #  it's open, and it's a keyword
                    print(f"The {self.direction} leads to {self.to_room.name}.")
        else:                     # there is a desciption set   
            closed = "(closed)" if not self.is_open else ""
            print(f"[ {self.direction} ]: {closed}\n  {self.description}")


class Room(Base):
    __tablename__ = "Rooms"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255), nullable=False)   

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

        objects = session.query(Object) \
                .join(RoomInventory, RoomInventory.object_id == Object.id) \
                .filter(RoomInventory.room_id == self.id) \
                .all()

        return objects if objects else []

    @property
    def mobiles(self):
        """
        Room.mobiles - list of all mobiles in the room
        """
        from mobiles import Mobile
        mobiles = session.query(Mobile) \
                .join(RoomMobiles, RoomMobiles.mobile_id == Mobile.id) \
                .filter(RoomMobiles.room_id == self.id) \
                .all()

        return mobiles if mobiles else []
    
    def look(self, viewer, **kwargs):
        """
        Displays the title, description, items, mobiles and exits of a given room.

        Args:
            viewer (Mobile): The player who is the doing the looking.
        Returns:
            None
        """
        room=self
        
        print(f"[ {room.name} ] ({room.id})")
        print(f"  {room.description}", end='')

            # List inventory in a natural way
        if room.inventory:
            if len(room.inventory) == 1:
                print(f" A solitary {room.inventory[0].name} rests here.")
            else:
                print(" Scattered about, you see a", end="")
                for i, obj in enumerate(room.inventory[:-1]):
                    print(f" {obj.name}", end=",")
                print(f" and a {room.inventory[-1].name}.")
        

        # List mobiles; filter out the player character
        other_mobiles = [mobile for mobile in room.mobiles if mobile.id != viewer.id]
        if other_mobiles:
            print(" Sharing the space with you ", end="")

            # Handle edge case: single mobile
            if len(other_mobiles) == 1:
                print(f"is {other_mobiles[0].name}.")

            else:
                print("are", end="")
                for i, mob in enumerate(other_mobiles[:-1]):
                    print(f" {mob.name}", end=",")
                print(f" and {other_mobiles[-1].name}.")
        
        if not other_mobiles and not room.inventory:
            print()

        print("  Obvious exits:\n[ ", end="")
        # list of non-hidden exits; cardinal directions added first, then keyword exits
        obvious_exits = [exit.direction for exit in self.exits if exit.direction in cardinals and exit.hidden==False]
        obvious_exits.extend([exit.direction for exit in self.exits if exit.direction not in cardinals and exit.hidden==False])
        if not obvious_exits:
            print('None')
        else:
            obvious_exits=", ".join(obvious_exits)
            print(obvious_exits, end="")
        print(" ]")


class RoomInventory(Base):
    __tablename__ = "Room_Inventory"

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("Rooms.id"), nullable=False)  
    object_id = Column(Integer, ForeignKey("Objects.id"), nullable=False)
    room = relationship("Room")
    object = relationship("Object")

class RoomMobiles(Base):
    from mobiles import Mobile
    __tablename__="Room_Mobiles"

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("Rooms.id"), nullable=False)  
    mobile_id = Column(Integer, ForeignKey("Mobiles.id"), nullable=False)  
    room = relationship("Room")
    mobile = relationship("Mobile")

    def __init__(self, room_id, mobile_id):
        self.room_id=room_id
        self.mobile_id=mobile_id


    def remove(target: Mobile) -> bool:
        """
        Removes the specified mobile from the current room by deleting the corresponding row in the RoomMobiles table.

        Args:
            target: The Mobile object representing the mobile to be removed.

        Returns:
            True if the mobile was removed successfully, False otherwise.
        """

        try:
            # Efficient deletion using session.query.delete() and filter by mobile_id
            session.query(RoomMobiles).filter(RoomMobiles.mobile_id == target.id).delete()
            session.commit()
            return True
        except Exception as e:
            # Handle potential errors gracefully
            session.rollback()
            print(f"Error removing mobile {target.name}: {e}")
            return False
        
def get_room_name_by_id(room_id: int) -> str:
    """Retrieves the name of a room based on its ID using SQLAlchemy."""
    result = session.query(Room.name).filter(Room.id == room_id).first()
    return result.name if result else "Unknown Room"  # Handle cases where room ID might not exist
