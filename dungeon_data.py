#dungeon_data.py

DATABASE = 'mysql+mariadbconnector://dm:dungeonmaster@localhost/dungeon'
DEBUG = False

# These imports are accessed by other modules:
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, MetaData, JSON, Boolean, and_, update, delete
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, joinedload

if DEBUG:
    engine = create_engine(DATABASE, echo=True)   
else:
    engine = create_engine(DATABASE, echo=False)

metadata = MetaData()
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()  # Establish base class for models
