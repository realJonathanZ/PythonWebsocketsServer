from typing import Set, Final

import asyncio
import websockets
import json
from websockets.asyncio.server import ServerConnection

# self-defined protocal.py
from protocal import ChatData, ChatPacket

# room contains 2 (or more?) clients of type ServerConnection, and can broadcast within the room
from room import Room


# global states ===
# =================
rooms: dict[str, Room] = {} 
DEFAULT_ROOM: Final[str] = "default_room" # const str of room id

# room handler ===
# =================


def get_or_create_room(room_id: str) -> Room:
    """
    get or create one room with given room id and return one Room instance.
    """
    if room_id not in rooms:
        a_room: Room = Room(room_id)
        rooms[room_id] = a_room
        print(f"created new room with id: {room_id}")
    else:
        a_room: Room = rooms[room_id]
        print(f"found existing room with id: {room_id}")

    return a_room

## NOTE: no longer allow clients broadcast/send packet via main server
# async def broadcast(sender: ServerConnection, message: str) -> None:
#     """
#     let the sender send one message and broadcast it out except to the sender itself.
#     @param message: a str, parsed json format.
#     # example about a message:
#     Suppose original unparsed json to be:
#     {
#         "type": "chat",
#         "data": {
#             "sender": "A",
#             "message": "Hello I'm A."
#         }
#     }
#     argument message will be a string like this:
#     '{"type": "chat", "data": {"sender": "A", "message": "Hello I'm A."}}'
#     """

#     disconnected_clients: Set[ServerConnection] = set() # store disconnected clients to remove them later

#     for client in list(connected_clients):
#         # sender do not send message to itself..
#         if client != sender:
#             # send the parsed json str message out
#             try:
#                 await client.send(message)

#             except Exception as e:
#                 print(f"WARNING: message send failed: {e}")
#                 # register this websocket connection as disconnected to the set.
#                 disconnected_clients.add(client)

#     # clean up dead connections..
#     for client in disconnected_clients:
#         connected_clients.discard(client) # discard(): more-safe remove()



async def handler(websocket: ServerConnection) -> None:
    """
    for each client connection that's made to this server,
    this handler function will be called to handle the connection.
    """

    # each client will get their own instance of this handler function.
    print("A client just connected")

    # assign to default room:
    room: Room = get_or_create_room(DEFAULT_ROOM)
    room.add_client(websocket)

    print(f"this lobby contains clients count: -> {len(room.clients)}")

    try:
        # this loop ends only when the WebSocket connection closes or an error happens. (for a particular ServerConncetion)
        async for message in websocket: # listen for messages from this client
            raw_message = message
            # parse json and print its contents (Only for logging and debugging purpose)
            try:
                packet: dict = json.loads(raw_message)  # Note: debugged point: check difference with .load() and .loads()

                # where TypedDict is invovlved, as example..
                if packet.get("type") == "chat":
                    chat_packet: ChatPacket = packet  # from dict to TypedDict

                    data: ChatData = chat_packet["data"]
                    sender: str = data["sender"]
                    chat_message: str = data["message"]

                    print(f"[RECEIVED][CHAT][{sender}]{chat_message}")


            except json.JSONDecodeError:
                print("main server received invalid json (or problem when loading):", raw_message)

            # broadcast, but only within the room.
            room.broadcast(raw_message, sender=websocket)


    except websockets.ConnectionClosed:
        # normal disconnect (no error) # happens when ctrl-c or crash
        pass

    except Exception as e:
        print("Unexpected error:", e)

    # when client disconnects...
    finally: # remove registered clent even if error occurs
        # which room? all rooms TODO need to trace in which rooms are clients disconnected?
        for r in rooms.values():
            r.remove_client(websocket)

        print("A client disconnected from one or more rooms")

        
        



async def main() -> None:
    server = await websockets.serve(
        handler,        # what runs when server started? # the handler function to handle incoming connections
        host = "localhost",    # who can connect? now: only this pc # host that listens on
        port = 8765            # port number? # port to listen on
    )

    print("WebSocket server running on ws://localhost:8765") # ws:// is the WebSocket protocol

    # await: process one message at a time for this ServerConnection instance(i.e. one client)
    await server.wait_closed() # don't exit, keep the server alive forever


asyncio.run(main()) # entry point: run the main function to start the server