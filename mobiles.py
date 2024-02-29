from dungeon_data import Base, Boolean, Column, Integer, String, relationship, ForeignKey, session, and_, delete
from objects import Object, ItemTypes
import actions

DEBUG=True
def debug(message): print(f'{__name__} *** DEBUG *** {message}') if DEBUG else None
debug(f'{DEBUG}')

# Mobile.type should be one of these:    
valid_mobile_types = [ "abberation", "animal", "construct", "dragon", "fey",
                        "fowl", "giant", "ghost", "goblinoid", "humanoid",
                        "monster", "orc", "skeleon", "troll", "undead",
                        "mobile", "player"]

class MobilePrototype(Base):
    __tablename__ = "Prototype_Mobiles"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    hp_max = Column(Integer, nullable=False)
    str=Column(Integer, nullable=False)
    dex=Column(Integer, nullable=False)
    int=Column(Integer, nullable=False)
    attack = Column(Integer, nullable=False)
    defense = Column(Integer, nullable=False)
    humanoid = Column(Boolean, nullable=False)
    description=Column(String)
    type = Column(String)

    def __init__(self, name, type=None, **kwargs):
        self.name = name
        if not type in valid_mobile_types: self.type="mobile"
        for key, value in kwargs.items:
            setattr(self, key, value)
        if self.hp_max: self.hp=self.hp_max

        session.add(self)
        session.commit()

class Mobile(Base):
    __tablename__ = "Mobiles"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    hp_max = Column(Integer, nullable=False)
    hp = Column(Integer, nullable=False)
    str=Column(Integer, nullable=False)
    dex=Column(Integer, nullable=False)
    int=Column(Integer, nullable=False)
    attack = Column(Integer, nullable=False)
    defense = Column(Integer, nullable=False)
    room_id = Column(Integer, ForeignKey("Rooms.id"))
        # do not update this directly; update the reference in RoomMobiles 
    humanoid = Column(Boolean, nullable=False)
    description=Column(String)
    type = Column(String)

    def __init__(self, name, type=None, hp_max=1, str=1, dex=1, int=1, attack=0, defense=0, humanoid=False, description=None, room_id=None, **kwargs):
        self.name = name
        self.type=type
        if not type in valid_mobile_types: self.type="mobile"
        self.hp_max=hp_max
        self.hp=self.hp_max
        self.str=str
        self.dex=dex
        self.int=int
        self.attack=attack
        self.defense=defense
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
        # make sure to update this in players.PlayerCharacter too!
        for item in self.equipment.values(): # unequip all items
            actions.do(self, "unequip", target=item)

        for item in self.inventory: # drop all items
            actions.do(self, "drop", target=item)
       
        # delete self from room
        from rooms import RoomMobiles
        session.execute(delete(RoomMobiles).filter_by(mobile_id=self.id))
        
        print(f"{self.name.capitalize()} is destroyed. Ashes to ashes, dust to dust.")

        # delete from database table:
        session.execute(delete(Mobile).filter_by(id=self.id))
            # (use a deconstructor?)
        session.commit()

    def __str__(self): return self.name

    def goto(self, to_room_id, silent=True):
        '''go to another room directly (by room.id)'''
        from dungeon_data import update
        from rooms import RoomMobiles
        #transfer to another room by ID
        session.execute(update(RoomMobiles)
                        .where(RoomMobiles.mobile_id==self.id)
                        .values(room_id=to_room_id))
        session.commit()
        if not silent: self.room.look(self)

    @property
    def inventory(self):
        """
        Returns a list of all objects in mobile's inventory.
        """
        objects = session.query(Object) \
                .join(MobileInventory, MobileInventory.object_id == Object.id) \
                .filter(MobileInventory.mobile_id == self.id) \
                .all()

        return objects if objects else []
        
    @property
    def equipment(self):
        """
        Returns a dictionary of all objects equipped by the mobile,
        using equipment type as the key and item reference as the value.
        """

        # 1. Get list of equipment types from ItemTypes.equipable==True:
        slots = [slot[0] for slot in session.query(ItemTypes.name).filter(ItemTypes.is_equipable == True).all()]  # Extract only slot names
        
        # 2. Initialize an empty dictionary for equipped items
        equipped_items = {}

        # 3. Loop through each equipment slot
        for slot in slots:
            # 4. Filter for equipment in the current slot
            # find the MobileEquipment where MobileEquipment.type == slot
            #                       and MobileEquipment.mobile_id == self.id
            #     then get the Object from Object where Object.id == object_id
            equipped_item=None
            equip=session.query(MobileEquipment).filter(MobileEquipment.mobile_id==self.id, MobileEquipment.type==slot).first()
            object_id = equip.object_id if equip else None
            if object_id: equipped_item=session.query(Object).filter(Object.id==object_id).first()

            # 5. Add the item to the dictionary, or None if no item is equipped
            equipped_items[slot] = equipped_item if equipped_item else None

        # 6. Return the dictionary of equipped items
        return equipped_items

    @property
    def room(self):
        from rooms import Room, RoomMobiles
        return session.query(Room).join(RoomMobiles, RoomMobiles.mobile_id == self.id).filter(RoomMobiles.room_id == Room.id).first()

    def look(self, **kwargs):
        """
        Displays the title, description, and exits of a given room.
        """
        if self.description:
            print(f"[ {self.name} ] ({self.id})")
            print(f"  {self.description}")
        else:
            print(f"It's just an ordinary {self.name}.")


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

    mobile_id = Column(Integer, ForeignKey("Mobiles.id"), primary_key=True)
    type = Column(String(255), ForeignKey("Item_Types.name"), primary_key=True)
    object_id = Column(Integer, ForeignKey("Objects.id"), nullable=False)

    def __str__(self):
        return f"{self.mobile_id}: {self.type} - {self.object_id}"
    