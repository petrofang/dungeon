#players.py

STARTING_ROOM=-1 # Heck

from dungeon_data import Base, Column, ForeignKey, Integer, JSON, String, session
from mobiles import Mobile
from rooms import RoomMobiles

class PlayerCharacter(Mobile): 
    __tablename__ = "Players"

    id = Column(Integer, ForeignKey("Mobiles.id"), primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    experience = Column(Integer, default=0)
    level = Column(Integer, default=1)
    skills = Column(JSON, nullable=True)
    stats = Column(JSON, nullable=True)

    def __init__(self, username:str, **kwargs):
        self.username=username
        super().__init__(username, **kwargs)

        self.id = -self.id # so players have negative IDs, easier to find on table
        self.hp_max=100
        self.hp=self.hp_max   
        self.humanoid=True
        self.experience=0
        self.level=1
        self.skills
        self.stats
        self.type="player"

        for key, value in kwargs.items():
            setattr(self, key, value)

        session.add(self)
        session.commit()

        # load player into starting room
        session.add(RoomMobiles(mobile_id=self.id, room_id=STARTING_ROOM))
        session.commit()

    def die(self):
        # what to do when a player dies... 
        print("You lose consciousness...")
        self.goto(-1)
        self.hp=self.hp_max

    def look(self, **kwargs):
        """
        Displays the name and description of a given player-character.
        """
        if self.description:
            print(f"[ {self.name} ] ({self.id})")
            print(f"  {self.description}")
        else:
            print(f"It's {self.name}, the player-character.")

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
            username = input("What is your name, adventurer?  > ", end="")
            if username:
                username = username.capitalize()
                # Check if username already exists
                if session.query(PlayerCharacter).filter_by(username=username).first():
                    print("That name is already taken.")
                else:
                    break
            else:
                print("\nPlease enter a name.  > ", end="")
    
    username = username.capitalize()    
    # Create new player instance with default values
    player = PlayerCharacter(username=username)

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
            username=username.capitalize()
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

    # make sure they are loaded back into the RoomMobiles table after logout:
    if not player.room_id: player.room_id=-1
    from rooms import RoomMobiles
    player_in_a_room = session.query(RoomMobiles).filter_by(mobile_id=player.id).first()

    if player_in_a_room:  # if player is already in a room (according to database)
        player_in_a_room.room_id = player.room_id  # Update room ID
    else:               # if not, add them to the database table:
        session.add(RoomMobiles(mobile_id=player.id, room_id=player.room_id))
        session.commit

    return player

def unload(self=None):
    """
    perform unload tasks for players-characters.
    """

    from rooms import RoomMobiles
    RoomMobiles.remove(target=self)
