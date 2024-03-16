import socket
from dungeon_data import Column, ForeignKey, Integer, JSON, String, session
from mobiles import Mobile
from rooms import RoomMobiles
import actions

STARTING_ROOM = -1 # Heck

player_sockets = {} # dictionary of connected sockets -- player.id:socket

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

    def load(self, socket):
        """
        any tasks or checks that need to be done when loading a player
        """   
        # add this player id to the player-sockets list
        player_sockets[self.id] = socket
        # move self to last known room
        self.goto(self.last_known_room_id 
                  if self.last_known_room_id 
                  else STARTING_ROOM)

    def unload(self):
        """
        perform unload tasks for players-characters.
        """
        # make sure last_known_room_id is set, then remove self from room
        self.last_known_room_id = self.room.id
        self.room.remove(target=self)

        # remove self from sockets dictionary, if still there
        if self.id in player_sockets.keys():
            player_sockets[self.id].close() # will this cause an error?
            player_sockets.pop(self.id)
        else:
            print(f"WARNING: {self.name} was already not in sockets list")

    def print(self, message = "", end="\n"):
        """
        Receives print statements and forwards them to the player's socket,
            if applicable.
        """
        try:
            if self.id in player_sockets.keys():
                socket = player_sockets[self.id]
                socket.send(f"{message}{end}".encode())
            else:
                print(f"socket not found for {self.name}, unloading player")
                self.unload()
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

    # add socket to active player list by player id
    player_sockets[player.id] = socket  
    return player

def get_player_by_id(id):
    player = session.query(
        PlayerCharacter).filter(PlayerCharacter.id == id).first()
    return player