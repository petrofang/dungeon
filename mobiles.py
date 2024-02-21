from dungeon_data import Base, Column, Integer, String, relationship, ForeignKey, session, and_
from objects import Object, ItemTypes

class Mobile(Base):
    __tablename__ = "Mobiles"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    hp_max = Column(Integer, nullable=False)
    hp = Column(Integer, nullable=False)
    attack = Column(Integer, nullable=False)
    defense = Column(Integer, nullable=False)

    def __str__(self): return self.name

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
            # Access the related Object using the equipment.item_id
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
            # Access the related Object using the equipment.item_id
            item = session.query(Object).get(equipment.object_id)
            return item
        else:
            return None









class MobileInventory(Base):
    __tablename__ = "Mobile_Inventory"

    id = Column(Integer, primary_key=True)
    mobile_id = Column(Integer, ForeignKey("Mobiles.id"), nullable=False)
    object_id = Column(Integer, ForeignKey("Objects.id"), nullable=False)
    quantity = Column(Integer, nullable=True, default=1)
    mobile = relationship("Mobile", backref="inventory")
    item = relationship("Object")

class MobileEquipment(Base):
    __tablename__ = "Mobile_Equipment"

    mobile_id = Column(Integer, ForeignKey("Mobiles.id"), primary_key=True)
    type = Column(String(255), ForeignKey("Item_Types.name"), primary_key=True)
    object_id = Column(Integer, ForeignKey("Objects.id"), nullable=False)

    # Relationship to ItemTypes for data access
    item_type = relationship("ItemTypes", backref="equipment")

    def __str__(self):
        return f"{self.mobile_id}: {self.item_type.name} - {self.item_id}"