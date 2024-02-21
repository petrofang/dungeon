#objects.py

from dungeon_data import Base, Column, Integer, String

class Object(Base):
    __tablename__ = "Objects"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)

    def __str__(self): return self.name

