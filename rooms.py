#rooms.py

DEBUG=True
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
    exits = relationship("Exit", backref="from_room", foreign_keys="[Exit.from_room_id]")

    @property
    def exits(self):
        """List of exits or None."""
        exits=session.query(Exit).filter(Exit.from_room_id == self.id).all()
        return exits

    @property
    def items(self):
        objects = session.query(Object) \
                .join(RoomInventory, RoomInventory.object_id == Object.id) \
                .filter(RoomInventory.room_id == self.id) \
                .all()

        return objects if objects else []

    @property
    def targets(self):
        """Room.targets - list of all mobile objects that can be targeted in the room"""
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
    room = relationship("Room", backref="inventory")
    object = relationship("Object")

class RoomMobiles(Base):
    from mobiles import Mobile
    __tablename__="Room_Mobiles"

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("Rooms.id"), nullable=False)  
    mobile_id = Column(Integer, ForeignKey("Mobiles.id"), nullable=False)  
    room = relationship("Room", backref="mobiles")
    mobile = relationship("Mobile")


def get_room_name_by_id(room_id: int, session: Session) -> str: # type: ignore
    """Retrieves the name of a room based on its ID using SQLAlchemy."""
    result = session.query(Room.name).filter(Room.id == room_id).first()
    return result.name if result else "Unknown Room"  # Handle cases where room ID might not exist

def look(room_id: int):
    
    from mobiles import Mobile
    """Displays the title, description, and exits of a given room.

    Args:
        room (Room): An instance of the Room model representing the room to display.

    Returns:
        None
    """
    
    room = session.query(Room).filter_by(id=room_id).first()
    if not room:
        print(f"Error: Room with ID {room_id} not found.")
        return
    
    print(f"[ {room.name} ]")
    print(f"{room.description}", end='')

    objects_in_room = session.query(Object).join(RoomInventory).filter(RoomInventory.room_id == room.id).all()
    mobiles_in_room = session.query(Mobile).join(RoomMobiles).filter(RoomMobiles.room_id == room.id).all()
    
    if objects_in_room:
        print(" Also", end ="")
        for obj in objects_in_room: print(f", {obj.name}", end="")
        print(".", end ='')
    
    if mobiles_in_room:
        print(" Joining you in the room", end='')
        for mob in mobiles_in_room: print(f": {mob.name} ", end='')
        print('...', end='')

    print("\nExits: ", end='')
    for exit in room.exits:  # Use the relationship to access exits
        print(f" {exit.direction.capitalize()} to {get_room_name_by_id(exit.to_room_id, session)}")

if __name__=="__main__": 
    rooms = session.query(Room).all()  # Query for all rooms    
    for each in rooms: look(each)