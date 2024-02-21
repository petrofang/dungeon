#dungeon_data.py

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
engine = create_engine('mysql+mariadbconnector://dm:dungeonmaster@localhost/dungeon')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()  # Establish base class for models
