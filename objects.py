from dungeon_data import Base, Column, Integer, String, Boolean, JSON
from dungeon_data import ForeignKey, session


class Container(Base):
    __tablename__ = "containers"
    container_id = Column(Integer, ForeignKey("objects.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("objects.id"), primary_key=True)

    def __init__(self, container, item):
        try:
            self.container_id = container.id
            if container.type != "container":
                raise TypeError(self, f"{container.name} is not a container.")
            elif container.id == item.id:
                raise RecursionError(self, "attemping to put item in itself.")
            self.item_id = item.id
        except:
            raise

class Object(Base):
    __tablename__ = "objects"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    description = Column(String)
    data = Column(JSON)

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
        return any(row.is_equipable for row in session.query(
            ItemTypes).filter(ItemTypes.name == self.type))
        
    def look(self, viewer):
        """
        Displays the name and description of the object.
        """
        if self.description:
            viewer.print(f"{self.name}:")
            viewer.print(f"  {self.description}")
        else:  
            viewer.print(f"It's just an ordinary {self.name}.", end=" ")
            # TODO: stats?

    def look_in(self, viewer):
        # TODO open/close containers
        # if not self.is_open: print("It is closed.")
        if not self.contents: # and self.is_open:
            viewer.print(f"A {self.name} appears to be empty.")
        else:
            viewer.print(f"A {self.name} contains", end=" ")
            if len(self.contents) == 1:
                viewer.print(f"nothing but a {self.contents[0].name}.")
            else:    
                for item in self.contents[:-1]:
                    viewer.print(f"a {item.name}", end=", ")
                viewer.print(f"and a {self.contents[-1].name}.")
        
    
    def put(self, item=None):
        """
        put an item into the object, if it is a container
        """
        if item and self.type == "container":
            session.add(Container(self, item))
            session.commit()

    def get(self, item=None):
        """ 
        remove an item from the container
        """
        if item and item in self.contents:
            containment = session.query(Container).filter(
                Container.item_id == item.id).first()
            if containment:
                session.delete(containment)
                session.commit()
                return item
            else:
                return None 
            
    @property
    def contents(self):
        if self.type != "container":
            return None
        else:
            my_items = session.query(Object).filter(
                Object.id == Container.item_id,
                Container.container_id == self.id
                ).all()
            return my_items if my_items else None
             
            
            
class ItemTypes(Base):
    __tablename__ = "item_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    is_equipable = Column(Boolean, default=False)

    def __str__(self):
        return self.name
    
