#objects.py

from dungeon_data import Base, Column, Integer, String, Boolean

class Object(Base):
    __tablename__ = "Objects"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)

    def __str__(self): return self.name

class ItemTypes(Base):
    __tablename__ = "Item_Types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    is_equipable = Column(Boolean, default=False)

    def __str__(self):
        return self.name