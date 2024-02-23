from dungeon_data import Base, Boolean, Column, Integer, String, relationship, ForeignKey, session, and_, delete
from objects import Object

DEBUG=False
def debug(message): print(f'{__name__} *** DEBUG *** {message}') if DEBUG else None
debug(f'{DEBUG}')

class Mobile(Base):
    __tablename__ = "Mobiles"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    hp_max = Column(Integer, nullable=False)
    hp = Column(Integer, nullable=False)
    attack = Column(Integer, nullable=False)
    defense = Column(Integer, nullable=False)
    room_id = Column(Integer, ForeignKey("Rooms.id"))
    humanoid = Column(Boolean, nullable=False)
    type = Column(String)

    def die(self): # make sure to update this in players.PlayerCharacter too!
        # what to do when a mobile dies... 
        from commands import CommandList
        # unequip all
        CommandList.unequip('all', self)
        # drop all
        CommandList.drop('all', self)
        # delete from room
        from rooms import RoomMobiles
        session.execute(delete(RoomMobiles).filter_by(mobile_id=self.id))
        # drop from database table
        session.execute(delete(Mobile).filter_by(id=self.id))
        session.commit()
        print(f"{self.name.capitalize()} is destroyed. Ashes to ashes, dust to dust.")

    def __str__(self): return self.name

    def goto(self, to_room_id, silent=True):
        '''go to another room directly (by room.id)'''
        from dungeon_data import update
        from rooms import RoomMobiles
        #transfer to another room by ID
        debug(f"mobile_id: {self.id}")
        debug(f"room_id:{to_room_id}")
        session.execute(update(RoomMobiles)
                        .where(RoomMobiles.mobile_id==self.id)
                        .values(room_id=to_room_id))
        session.commit()
        debug(f"me.room_id={self.room_id}")

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
        object_list = []
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
        from rooms import Room
        return session.query(Room).filter_by(id=self.room_id).first()






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

    def __str__(self):
        return f"{self.mobile_id}: {self.type} - {self.object_id}"