from dungeon_data import Column, ForeignKey, Integer, JSON, String, session
from mobiles import Mobile
from rooms import RoomMobiles

STARTING_ROOM=-1 # Heck


class PlayerCharacter(Mobile): 
    __tablename__ = "players"

    id = Column(Integer, ForeignKey("mobiles.id"), primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    experience = Column(Integer, default=0)
    level = Column(Integer, default=1)
    skills = Column(JSON, nullable=True)
    stats = Column(JSON, nullable=True)
    last_known_room_id = Column(Integer)

    def __init__(self, username:str, **kwargs):
        self.username=username
        self.last_known_room_id=STARTING_ROOM
        super().__init__(username, **kwargs)

        self.id = -self.id # negative IDs help with sorting on Mobiles table
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
        username: The desired username for the player. 
            If None, prompts the user.

    Returns:
        A Player object representing the new character.
    """

    if username is None:
        # Prompt for username
        while True:
            username = input("What is your name, adventurer?  > ")
            if username:
                username = username.capitalize()
                # Check if username already exists
                if session.query(
                        PlayerCharacter).filter_by(
                        username=username).first():
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
    """
    if username is None:
        # Prompt for username
        while True:
            username = input("Player to load > ")
            username=username.capitalize()
            if username:
                # Check if username doesn't already exist:
                if not session.query(
                        PlayerCharacter).filter_by(
                        username=username).first():
                    print("username not found.")
                    newb=input("would you like to make a new character, ",
                               f"{username}? (Y/N) > ")
                    if newb:
                        if newb.upper()[0]=="Y": 
                            return new(username)
                else:
                    break
            else:
                print("Please enter a name.")
    player = session.query(PlayerCharacter
                           ).filter_by(username=username).first()

    # ensure Player.room_id and RoomMobiles.room_id are synchronized:

    # there 'should' be a room_id set, but if not:
    if not player.room_id: player.room_id=-1
    player.goto(player.last_known_room_id)
    
    return player

def unload(self=None):
    """
    perform unload tasks for players-characters.
    """

    RoomMobiles.remove(target=self)
