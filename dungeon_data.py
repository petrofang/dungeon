from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy import MetaData, JSON, Boolean, and_, update, delete
# Some of these imports are accessed by other modules which import from here.

# DATABASE = 'mysql+mariadbconnector://dm:dungeonmaster@localhost/dungeon'
DATABASE = 'sqlite:///dungeon.db'
# TODO : take this out of hardcode and put in config file with .gitignore
# TODO : maybe use SQLite instead???

VERBOSE = False

if VERBOSE:
    engine = create_engine(DATABASE, echo=True)   
else:
    engine = create_engine(DATABASE, echo=False)

metadata = MetaData()
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()
