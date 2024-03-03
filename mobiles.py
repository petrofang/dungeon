from dungeon_data import Base, Boolean, Column, delete, ForeignKey, Integer 
from dungeon_data import JSON, relationship, session, String, update
import actions
from objects import Object, ItemTypes

# Mobile.type should be one of these:    
valid_mobile_types = [ "abberation", "animal", "construct", "dragon", "fey",
                        "fowl", "giant", "ghost", "goblinoid", "humanoid",
                        "monster", "orc", "skeleon", "troll", "undead",
                        "mobile", "player"]

       

class Mobile(Base):
    __tablename__ = "Mobiles"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    hp_max = Column(Integer, nullable=False)
    hp = Column(Integer, nullable=False)
    str = Column(Integer, nullable=False)
    dex = Column(Integer, nullable=False)
    int = Column(Integer, nullable=False)
    room_id = Column(Integer, ForeignKey("Rooms.id"))
        # room_id represents where the mobile is "supposed" to be.
        # most operations by the game engine use RoomMobiles table.
        # room_id is necessary for logged-off players who are not 
        # on the RoomMobiles table. TODO: fix this (last_known_room)?
    humanoid = Column(Boolean, nullable=False)
    description = Column(String)
    type = Column(String)

    def __init__(self, name, type=None, hp_max=1, str=1, dex=1, int=1,
                humanoid=False, description=None,
                 room_id=None, **kwargs):
        self.name = name
        self.type=type
        if not type in valid_mobile_types: self.type="mobile"
        self.hp_max=hp_max
        self.hp=self.hp_max
        self.str=str
        self.dex=dex
        self.int=int
        self.humanoid=humanoid
        self.description=description
        self.room_id=room_id
        if self.room_id:
            from rooms import RoomMobiles
            RoomMobiles(self.room_id, self.id)

        for key, value in kwargs.items():
            setattr(self, key, value)
        
        session.add(self)
        session.commit()
         
    def die(self): 
        for item in self.equipment.values(): # unequip all items
            actions.do(self, "unequip", target=item)

        for item in self.inventory: # drop all items
            actions.do(self, "drop", target=item)
       
        # delete self from room
        from rooms import RoomMobiles
        session.execute(delete(RoomMobiles).filter_by(mobile_id=self.id))
        
        print(f"{self.name.capitalize()} is destroyed. ",
              "Ashes to ashes, dust to dust.")

        # delete from database table:
        session.execute(delete(Mobile).filter_by(id=self.id))
            # (use a deconstructor?)
        session.commit()

    def __str__(self): return self.name

    def goto(self, to_room_id, silent=True):
        """
        Go to another room directly (by room.id)
        
        Note that a trigger in the MySQL database will automatically
            update Player.room_id based on the change to RoomMobiles.room_id
        
        This will need to be changed if using a different database
            which does not have triggers (eg SQLite)
        """

        from rooms import RoomMobiles
        #transfer to another room by ID
        present = session.query(
            RoomMobiles).filter(RoomMobiles.mobile_id==self.id).first()
        if present:
            session.execute(
                update(RoomMobiles
                ).where(RoomMobiles.mobile_id==self.id
                ).values(room_id=to_room_id))
        else:
            session.add(RoomMobiles(to_room_id, self.id))
        session.commit()

        if not silent: self.room.look(self)

    @property
    def inventory(self):
        """
        Returns a list of all objects in mobile's inventory.
        """
        objects = session.query(Object).join(MobileInventory, 
            MobileInventory.object_id == Object.id
            ).filter(MobileInventory.mobile_id == self.id).all()
        return objects if objects else []
        
    @property
    def equipment(self):
        """
        Returns a dictionary of all objects equipped by the mobile,
        using equipment type as the key and item Object as the value.
            eg:
                self.equipment['weapon'] = Object('sword', 'weapon')
                self.equipment['armor'] = Object('leathers, 'armor')
                damage = self.equipment['weapon'].rating 
                for equipment in self.equipment.values(): ...
        """

        # 1. Get list of equipment types from ItemTypes.equipable==True:
        slots = [slot[0] for slot in session.query(ItemTypes.name
            ).filter(ItemTypes.is_equipable == True).all()]
        
        # 2. Initialize an empty dictionary for equipped items
        equipped_items = {}

        # 3. Loop through each equipment slot
        for slot in slots:
            # 4. find the id of the equipment in the current slot or None
            equipped_item = None
            equip = session.query(MobileEquipment).filter(
                MobileEquipment.mobile_id==self.id, 
                MobileEquipment.type==slot).first()
            object_id = equip.object_id if equip else None
            if object_id: equipped_item=session.query(Object).filter(
                Object.id==object_id).first()

            # 5. Add the item to the dictionary, or None
            equipped_items[slot] = equipped_item

        # 6. Return the dictionary of equipped items
        return equipped_items

    @property
    def room(self):
        from rooms import Room, RoomMobiles
        return session.query(Room).join(RoomMobiles, 
            RoomMobiles.mobile_id == self.id).filter(
            RoomMobiles.room_id == Room.id).first()

    def look(self, **kwargs):
        """
        Displays the name and description of a given mobile.
        """
        if self.description:
            print(f"[ {self.name} ] ({self.id})")
            print(f"  {self.description}")
        else:
            print(f"It's just an ordinary {self.name}.")


class MobilePrototype(Base):
    """
    A prototype mobile which can be used to spawn functional mobiles
    """
    __tablename__ = "Prototype_Mobiles"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    hp_max = Column(Integer, nullable=False)
    str = Column(Integer, nullable=False)
    dex = Column(Integer, nullable=False)
    int = Column(Integer, nullable=False)
    humanoid = Column(Boolean, nullable=False)
    description = Column(String)
    type = Column(String)

    def __init__(self, name, type=None, **kwargs):
        self.name = name
        if not type in valid_mobile_types: self.type="mobile"
        for key, value in kwargs.items:
            setattr(self, key, value)
        if self.hp_max: self.hp=self.hp_max

        session.add(self)
        session.commit()

    def spawn(self, invoker:Mobile = None):
        room_id = invoker.room_id if invoker.room_id else invoker.id
        # BUG (maybe?) -- might this cause mobs to spawn wrong room?
        
        spawn = Mobile(name=self.name, type=self.type, hp_max=self.hp_max, 
            str=self.str, dex=self.dex, int=self.int, humanoid=self.humanoid,
            description=self.description)
        spawn.goto(room_id)
        session.add(spawn)
        session.commit()
 
class MobileInventory(Base):
    __tablename__ = "Mobile_Inventory"

    id = Column(Integer, primary_key=True)
    mobile_id = Column(Integer, ForeignKey("Mobiles.id"), nullable=False)
    object_id = Column(Integer, ForeignKey("Objects.id"), nullable=False)
    quantity = Column(Integer, nullable=True, default=1)
    mobile = relationship("Mobile")
    item = relationship("Object")


class MobileEquipment(Base):
    __tablename__ = "Mobile_Equipment"

    mobile_id = Column(Integer, 
        ForeignKey("Mobiles.id"), primary_key=True)
    type = Column(String(255), 
        ForeignKey("Item_Types.name"), primary_key=True)
    object_id = Column(Integer, 
        ForeignKey("Objects.id"), nullable=False)

    def __str__(self):
        return f"{self.mobile_id}: {self.type} - {self.object_id}"
    