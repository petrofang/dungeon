from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy import MetaData, JSON, Boolean, and_, update, delete
# Some of these imports are accessed in chain by other modules.

DATABASE = 'mysql+mariadbconnector://dm:dungeonmaster@localhost/dungeon'
VERBOSE = False

if VERBOSE:
    engine = create_engine(DATABASE, echo=True)   
else:
    engine = create_engine(DATABASE, echo=False)

metadata = MetaData()
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()  # Establish base class for models
