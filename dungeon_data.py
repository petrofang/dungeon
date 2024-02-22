#dungeon_data.py

DATABASE = 'mysql+mariadbconnector://dm:dungeonmaster@localhost/dungeon'
DEBUG = False

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, MetaData, JSON, Boolean, and_, update
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, joinedload
if DEBUG:
    engine = create_engine(DATABASE, echo=True)   
else:
    engine = create_engine(DATABASE, echo=False)


Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()  # Establish base class for models
