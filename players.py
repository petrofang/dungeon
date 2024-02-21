#players.py

DEBUG=False
def debug(message): print(f'{__name__} DEBUG: {message}') if DEBUG else None
debug(f'{DEBUG}')

from dungeon_data import Base, Column, Session, engine, ForeignKey, Integer, JSON, String, sessionmaker, session
from mobiles import Mobile
from rooms import Room

class PlayerCharacter(Mobile):
    __tablename__ = "Players"

    id = Column(Integer, ForeignKey("Mobiles.id"), primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    experience = Column(Integer, default=0)
    level = Column(Integer, default=1)
    skills = Column(JSON, nullable=True)
    stats = Column(JSON, nullable=True)
    room_id = Column(Integer, ForeignKey("Rooms.id"))

    def room(self) -> Room:
        return session.query(Room).filter_by(id=self.room_id).first()

#TODO: add case-insensitive checks for new/load players.
def new(username: str = None) -> PlayerCharacter:
    """
    Creates a new player character.

    Args:
        username: The desired username for the player. If None, prompts the user.

    Returns:
        A Player object representing the new character.
    """

    if username is None:
        # Prompt for username
        while True:
            username = input("What is your name, adventurer? > ")
            if username:
                # Check if username already exists
                if session.query(PlayerCharacter).filter_by(username=username).first():
                    print("That name is already taken.")
                else:
                    break
            else:
                print("Please enter a name.")
        
    # Create new player instance with default values
    player = PlayerCharacter(username=username)

    # Set initial values for additional attributes (optional)
    player.hp_max = 100
    player.hp = 100
    player.attack = 2
    player.defense = 2
    player.name=username
    player.room_id = 1 # set this to a starting area

    # Save the new player to the database
    session.add(player)
    session.commit()

    # Inform the user and return the new player
    print(f"Welcome to the game, {username}!")
    return player

def load(username: str = None) -> PlayerCharacter: # type: ignore
    """
    Loads a player from the database based on their username.

    Args:
        username (str): The username of the player to load.
        session: A SQLAlchemy session object for database interaction.

    Returns:
        Player: The Player object representing the loaded character, or None if not found.
    """
    if username is None:
        # Prompt for username
        while True:
            username = input("Player to load > ")
            if username:
                # Check if username doesn't already exist:
                if not session.query(PlayerCharacter).filter_by(username=username).first():
                    print("username not found.")
                    newb=input(f"would you like to make a new character, {username}? (Y/N) > ")
                    if newb:
                        if newb.upper()[0]=="Y": 
                            return new(username)
                else:
                    break
            else:
                print("Please enter a name.")
    player = session.query(PlayerCharacter).filter_by(username=username).first()
    return player

if __name__=="__main__": new("Rogue")