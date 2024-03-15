import socket
import threading
import miniupnpc

from dungeon_data import session
import commands
import players

HOST = "localhost"
PORT = 4000
MAX_CONNECTIONS = 5
PROMPT=' >> '

splash_screen = r"""
     _  Eventually, there may be a                                
  __| |_   _ _ __   __ _  ___  ___  _ __  
 / _` | | | | '_ \ / _` |/ _ \/ _ \| '_ \ 
| (_| | |_| | | | | (_| |  __/ (_) | | | |
 \__,_|\__,_|_| |_|\__, |\___|\___/|_| |_|
                   |___/ (c)2024 Petrofang                  
"""
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def start_game_server():
    # open a server socket for listening
    print(f"initializing server...")
    print(f"host: {HOST}")
    print(f"port: {PORT}")
    print(f"max connections: {MAX_CONNECTIONS}")
    try:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        server.bind((HOST, PORT))
        server.listen(MAX_CONNECTIONS)
    except Exception:
        print(f"Unable to start server: \n{Exception.with_traceback()}")
        server.close()
        quit()

def enable_upnp_port_mapping():
    # uPnP: port mapping
    try:
        upnp = miniupnpc.UPnP()
        upnp.discoverdelay = 10
        upnp.discover()
        # addportmapping(external-port, protocol, internal-host, internal-port, description, remote-host)
        upnp.addportmapping(PORT, 'TCP', upnp.lanaddr, PORT, 'dungeon', '')
        print("Universal Plug-n-Play successfully enabled.")
    except: 
        print("Universal Plug-n-Play could not be enabled!")
        print("  Please check the Gateway (http://10.0.0.1) ")

def send(socket, message="", end="\n"):
    """
    send message to a connected socket
    """
    socket.send(f"{message}{end}".encode())

def receive(socket):
    user_input = socket.recv(1024).decode()
    return user_input

def wait_for_connections():
    """
    receive player connections and hand them off to the handler.
    """
    while True: # wait for connection:
        socket, address = server.accept()
        print(f"connection: {address}")
        print(f"  {socket}")
        send(socket, splash_screen)
        send(socket, 'What is your name, adventurer?  >> ')
        name = receive(socket)
        name = name.strip().capitalize()
        player = session.query(
            players.PlayerCharacter).filter_by(
            username = name).first()
        
        if player:
            send(socket, f"Password for {player.name}:  ")
            password = receive(socket)
            # TODO: Password hashing and verification here
            send(socket, "TODO: *actually* check the password")

        elif not player:
            # TODO: Character creation
            send(socket, f"Player '{name}' unknown.")
            send(socket, f"Would you like to create a character? (Y)es / (N)o")
            yes = receive(socket)
            if yes[0].lower() == "y":
                player = players.new(socket, name)
        if not player: # still? ... hey, we tried!
            socket.close()
        else:
            player.socket=socket
            print(f"{address[0]} has loaded player {player.name}")
            player.load()
            connection_thread = threading.Thread(
                target=handle_connection,
                args = (player,))
            connection_thread.start()

def handle_connection(player:players.PlayerCharacter):
    """
    handler for player-connection sockets
    """    
    player.print(f'Hint: type HELP for a list of commands')
        
    while True:
        try:
            send(player.socket, PROMPT, end="")
            user_input = receive(player.socket)
            user_input = user_input.strip()
            commands.parse(player, user_input)
        except Exception:
            if player in players.connections:
                players.connections.remove(player)
                print(f"{player} removed from connections.")
            else: print(f"{player} was not listed in connections (?)")
            player.unload()
            player.socket.close()
            print(f"{player} has left the realm.")

if __name__=="__main__": 
    print("Execute main.py, not this.")
    quit()
