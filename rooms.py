#rooms.py

DEBUG=False
def debug(message): print(f'{__name__} *** DEBUG *** {message}') if DEBUG else None
debug(f'{DEBUG}')

from dungeon_data import Base, Column, Integer, ForeignKey, String, relationship, Session, session
from objects import Object


class Exit(Base):
    __tablename__ = "Exits"

    from_room_id = Column(Integer, ForeignKey("Rooms.id"), primary_key=True)
    to_room_id = Column(Integer, ForeignKey("Rooms.id"), primary_key=True)
    direction = Column(String(10), nullable=False)
    
    # Add additional attributes if needed (e.g., description, locked)

class Room(Base):
    __tablename__ = "Rooms"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255), nullable=False)   
#    exits = relationship("Exit", backref="from_room", foreign_keys="[Exit.from_room_id]")

    @property
    def exits(self):
        """List of exits or None."""
        exits=session.query(Exit).filter(Exit.from_room_id == self.id).all()
        return exits

    @property
    def inventory(self):
        objects = session.query(Object) \
                .join(RoomInventory, RoomInventory.object_id == Object.id) \
                .filter(RoomInventory.room_id == self.id) \
                .all()

        return objects if objects else []

    @property
    def mobiles(self):
        """Room.mobiles - list of all mobile objects that can be targeted in the room"""
        from mobiles import Mobile
        mobiles = session.query(Mobile) \
                .join(RoomMobiles, RoomMobiles.mobile_id == Mobile.id) \
                .filter(RoomMobiles.room_id == self.id) \
                .all()

        return mobiles if mobiles else []

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

def look(me):
    """Displays the title, description, and exits of a given room.

    Args:
        me  (Mobile): The player who is the doing the looking.
    Returns:
        None
    """
    room = me.room
    if not room:
        print(f"Error: Room not found.")
        return
    
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
    

    # Filter out the player character
    other_mobiles = [mobile for mobile in room.mobiles if mobile.id != me.id]
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
    print("    Exits:")
    for exit in room.exits: 
        print(f" {exit.direction.capitalize()} to {get_room_name_by_id(exit.to_room_id)} ")
