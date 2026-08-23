## This is a logic container not involving networking yet.
## 1 room will hold 2 players(for now!)

import asyncio
from typing import Set
from websockets.asyncio.server import ServerConnection

class Room:
    """
    A simple room containing 2 websocket clients, of type ServerConnection.
    @constructor: room_id: str, a unique id for this room.
    clients: Set[ServerConnection], a set of 2 clients in this room.
    """
    def __init__(self, room_id: str):
        self.room_id: str = room_id                  # room id e.x. "24251"
        self.clients: Set[ServerConnection] = set()  # containing 2 connections, passed from main server.

    def add_client(self, client: ServerConnection) -> None:
        self.clients.add(client)
        print(f"[ROOM {self.room_id}] one client joined in room \
              . remaining total={len(self.clients)}")

    def remove_client(self, client: ServerConnection) -> None:
        self.clients.discard(client)
        print(f"[ROOM {self.room_id}] one client left from room \
              . remaining total={len(self.clients)}")
        
    async def broadcast(self, message: str, sender: ServerConnection = None) -> None:
        """
        send A message to all other clients in THIS room except self.
        @param message: a str, parsed json format.
        """

        disconnected_client_connections: Set[ServerConnection] = set()  # to store clients that failed to send message

        for client_connection in list(self.clients):
            if sender and client_connection == sender:
                continue
            
            # othewise, iterated on client that's not self
            try:
                await client_connection.send(message) # here client_connection represents the server's end from
                # the ServerConnection between server and client.
                # meaning send message through the particular connection from server end to client end.

            except Exception as e:
                print(f"Error: [ROOM {self.room_id}] message-sending failed, Error: {e}")
            
                disconnected_client_connections.add(client_connection)

        for client_connection in disconnected_client_connections:
            self.clients.discard(client_connection)  # remove disconnected clients from the room
            