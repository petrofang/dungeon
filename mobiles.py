from dungeon_data import Base, Column, Integer, String, relationship, ForeignKey

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

    def __str__(self): return self.name

class MobileInventory(Base):
    __tablename__ = "Mobile_Inventory"

    id = Column(Integer, primary_key=True)
    mobile_id = Column(Integer, ForeignKey("Mobiles.id"), nullable=False)
    object_id = Column(Integer, ForeignKey("Objects.id"), nullable=False)
    quantity = Column(Integer, nullable=True, default=1)
    mobile = relationship("Mobile", backref="inventory")
    item = relationship("Object")