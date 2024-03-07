import socket
from dungeon_data import Column, ForeignKey, Integer, JSON, String, session
from mobiles import Mobile
from rooms import RoomMobiles
import actions

STARTING_ROOM=-1 # Heck

connections = [] # List of connected players (player objects)

class PlayerCharacter(Mobile): 
    __tablename__ = "players"

    id = Column(Integer, ForeignKey("mobiles.id"), primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    experience = Column(Integer, default=0)
    level = Column(Integer, default=1)
    skills = Column(JSON, nullable=True)
    stats = Column(JSON, nullable=True)
    last_known_room_id = Column(Integer)

    def __init__(self, username:str, socket:socket.socket, **kwargs):
        super().__init__(username, **kwargs)
        self.last_known_room_id = STARTING_ROOM
        self.socket = socket # socket
        self.username = username
        self.hp_max = 100
        self.hp = self.hp_max   
        self.humanoid = True
        self.experience = 0
        self.level = 1
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
        actions.echo_at(self, "You lose consciousness...")
        actions.echo_around(self, f"{self} has lost consciousness!")
        self.goto(-1)
        self.hp=self.hp_max

    def look(self, viewer):
        """
        Displays the name and description of a given player-character.
        """
        if self.description:
            viewer.print(f"[ {self.name} ] ({self.id})")
            viewer.print(f"  {self.description}")
        else:
            viewer.print(f"It's {self.name}, a fellow adventurer.")

    def load(self):
        """
        any tasks or checks that need to be done when loading a player
        """   
        connections.append(self) 
        self.goto(self.last_known_room_id if self.last_known_room_id else -1)

    def unload(player=None):
        """
        perform unload tasks for players-characters.
        """
        if player in connections: connections.remove(player)
        player.room.remove(target=player)
        player.socket.close()

    def print(self, message = "", end="\n"):
        """
        Receives print statements and forwards them to the player's socket,
            if applicable.
        """
        try:
            self.socket.send(f"{message}{end}".encode())
        except:
            print(f"error sending to {self.name}'s socket:")
            print(f"{message}")


def new(socket, username) -> PlayerCharacter:
    """
    Creates a new player character.

    Args:
        username: The desired username for the player. 
            If None, prompts the user.

    Returns:
        A Player object representing the new character.
    """

    username = username.capitalize()
    # Create new player instance with default values
    player = PlayerCharacter(username=username, socket=socket)

    session.add(player)
    session.commit()

    # Inform the user and return the new player
    player.print(f"Welcome home, {username}!")
    return player
