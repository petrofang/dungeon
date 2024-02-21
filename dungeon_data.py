#dungeon_data.py

DATABASE = 'mysql+mariadbconnector://dm:dungeonmaster@localhost/dungeon'

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, JSON, Boolean, and_
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, joinedload
engine = create_engine(DATABASE)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()  # Establish base class for models
