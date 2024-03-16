from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy import MetaData, JSON, Boolean, and_, update, delete
# Some of these imports are accessed by other modules which import from here.

VERBOSE = False
DATABASE = 'sqlite:///dungeon.db'

engine = create_engine(DATABASE, echo=True if VERBOSE else False) 


metadata = MetaData()
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()
