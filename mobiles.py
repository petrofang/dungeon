from dungeon_data import Base, Boolean, Column, Integer, String, relationship, ForeignKey, session, and_, delete
from objects import Object
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
        for item in self.equipment: # unequip all items
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
        Returns a list of all objects equipped by the mobile.

        This includes items of any type equipped in any slot.
        """
        equipped_items = session.query(MobileEquipment).filter(MobileEquipment.mobile_id == self.id).all()
        object_list = []         #TODO: update this to a dictionary {equipment.type = item_reference}
        for equipment in equipped_items:
            item = session.query(Object).get(equipment.object_id)
            if item:  # Handle potential None values
                object_list.append(item)
        return object_list

    @property
    def weapon(self):
        """Retrieves the equipped weapon or None."""
        equipment = session.query(MobileEquipment).filter(and_(MobileEquipment.mobile_id == self.id, MobileEquipment.type == "weapon")).first()
        if equipment:
            item = session.query(Object).get(equipment.object_id)
            return item
        else:
            return None

    @property
    def shield(self):
        """Retrieves the equipped shield or None."""
        equipment = session.query(MobileEquipment).filter(
            and_(MobileEquipment.mobile_id == self.id, MobileEquipment.type == "shield")
        ).first()
        if equipment:
            # Access the related Object using the equipment.object_id
            item = session.query(Object).get(equipment.object_id)
            return item
        else:
            return None

    @property
    def armor(self):
        """Retrieves the equipped armor or None."""
        equipment = session.query(MobileEquipment).filter(
            and_(MobileEquipment.mobile_id == self.id, MobileEquipment.type == "armor")
        ).first()

        if equipment:
            # Access the related Object using the equipment.object_id
            item = session.query(Object).get(equipment.object_id)
            return item
        else:
            return None

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

    # Relationship to ItemTypes for data access
    item_type = relationship("ItemTypes", backref="equipment") 
    # is this right?

    def __str__(self):
        return f"{self.mobile_id}: {self.type} - {self.object_id}"
    