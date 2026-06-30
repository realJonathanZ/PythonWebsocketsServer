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
        
    def broadcast(self, message: str, sender: ServerConnection = None) -> None:
        """
        send A message to all other clients in THIS room except self.
        @param message: a str, parsed json format.
        """

        for client in list(self.clients):
            if sender and client == sender:
                continue
            
            # othewise, iterated on client that's not self
            try:
                # TODO: need change
                asyncio.create_task(client.send(message))

            except Exception as e:
                print(f"Error: [ROOM {self.room_id}] message-sending failed, Error: {e}")
                self.clients.discard(client)  # remove from this room