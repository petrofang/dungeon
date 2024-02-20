#rooms.py

DEBUG=False
INFO=False
def debug(message): print(f'{__name__} DEBUG: {message}') if DEBUG else None
def info(message):  print(f'{__name__} INFO: {message}')  if INFO  else None
debug(f'{DEBUG}')
info(f'{INFO}')

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

engine = create_engine('mysql+pymysql://dm:dungeonmaster@localhost/dungeon')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()  # Establish base class for models
Base.metadata.create_all(engine)  # Create tables

class Mobile(Base):
    __tablename__ = "Mobiles"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    hp_max = Column(Integer, nullable=False)
    hp = Column(Integer, nullable=False)
    attack = Column(Integer, nullable=False)
    defense = Column(Integer, nullable=False)
    weapon = Column(Integer)
    shield = Column(Integer)
    armor = Column(Integer)

class Object(Base):
    __tablename__ = "Objects"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)

    def __str__(self): return self.name
objects = session.query(Object).all()

mobiles = session.query(Mobile).all()


class Exit(Base):
    __tablename__ = "Exits"

    from_room_id = Column(Integer, ForeignKey("Rooms.id"), primary_key=True)
    to_room_id = Column(Integer, ForeignKey("Rooms.id"), primary_key=True)
    direction = Column(String(10), nullable=False)
    
    # Add additional attributes if needed (e.g., description, locked)

class Room(Base):
    __tablename__ = "Rooms"  # Ensure consistent table name

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255), nullable=False)   
    exits = relationship("Exit", backref="from_room", foreign_keys="[Exit.from_room_id]")
Rooms = session.query(Room).all()  # Query for all rooms    

class RoomInventory(Base):
    __tablename__ = "Room_Inventory"

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("Rooms.id"), nullable=False)  
    object_id = Column(Integer, ForeignKey("Objects.id"), nullable=False)
    room = relationship("Room", backref="inventory")
    object = relationship("Object")

class RoomMobiles(Base):
    __tablename__="Room_Mobiles"

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("Rooms.id"), nullable=False)  
    mobile_id = Column(Integer, ForeignKey("Mobiles.id"), nullable=False)  
    room = relationship("Room", backref="mobiles")
    mobile = relationship("Mobile") # BUG: why doesn't this work when Mobile is imported, 
                                    # but does when it's pasted into this module?

class MobileInventory(Base):
    __tablename__ = "Mobile_Inventory"

    id = Column(Integer, primary_key=True)
    mobile_id = Column(Integer, ForeignKey("Mobiles.id"), nullable=False)
    object_id = Column(Integer, ForeignKey("Objects.id"), nullable=False)
    quantity = Column(Integer, nullable=True, default=1)
    mobile = relationship("Mobile", backref="inventory")
    item = relationship("Object")

def get_room_name_by_id(room_id: int, session: Session) -> str: # type: ignore
    """Retrieves the name of a room based on its ID using SQLAlchemy."""
    result = session.query(Room.name).filter(Room.id == room_id).first()
    return result.name if result else "Unknown Room"  # Handle cases where room ID might not exist

def display_room_info(room: Room):
    """Displays the title, description, and exits of a given room.

    Args:
        room (Room): An instance of the Room model representing the room to display.

    Returns:
        None
    """

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

    # Iterate and display retrieved objects
def main():
    # Display all rooms using a loop
    for room in Rooms:
        display_room_info(room)

    # Add other game logic here...

if __name__ == "__main__":
    main()
