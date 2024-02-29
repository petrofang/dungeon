#objects.py

from dungeon_data import Base, Column, Integer, String, Boolean

class Object(Base):
    __tablename__ = "Objects"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    description = Column(String)

    def __init__(self, name:str="item", type:str="item", rating=0, **kwargs):
        self.name=name
        self.rating=rating
        if type in ItemTypes:
            self.type=type
        else:
            self.type="item"
        for key, value in kwargs.items:
            setattr(self, key, value)

    def __str__(self): return self.name

    @property
    def is_equipable(self):
        from dungeon_data import session
        """
        Checks if the current object is equipable based on its type.

        Returns:
            True if the object is equipable, False otherwise.
        """
        return any(row.is_equipable for row in session.query(ItemTypes).filter(ItemTypes.name == self.type))
        
    def look(self, **kwargs):
        """
        Displays the title, description, and exits of a given room.
        """
        if self.description:
            print(f"[ {self.name} ] ({self.id})")
            print(f"  {self.description}")
        else:
            print(f"It's just an ordinary {self.name}.")
            
class ItemTypes(Base):
    __tablename__ = "Item_Types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    is_equipable = Column(Boolean, default=False)

    def __str__(self):
        return self.name