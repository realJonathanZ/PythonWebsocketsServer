from typing import  Final

import asyncio
import websockets
import json
from websockets.asyncio.server import ServerConnection

# for curiosity for the time between 2 polls in godot _process() where it polls for every process frame..
import time


# self-defined protocal.py
from protocal import (
    ChatPacket, ChatData,
    JoinRoomPacket, JoinRoomData,
    RoomJoinedPacket, RoomJoinedData,
)

# room contains 0, 1, 2 (or more?) clients of type ServerConnection, and can broadcast within the room
from room import Room

# Validation functions before incoming packet(s) being indexed in.
from json_validation import parse_chat_packet, parse_join_room_packet


# global states ===
# =================
rooms: dict[str, Room] = {} 
# NOTE: might only let one client to be in one "Room" for now..
client_to_room: dict[ServerConnection, Room] = {} # map each client to its room
DEFAULT_ROOM: Final[str] = "default_room" # const str of room id

# Room related helper funcs ===
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


def get_current_room(client: ServerConnection) -> Room | None:
    """
    get the Room that this client is currently in, or None if not in any room. 
    (note: maximum one room for this client to stay)
    """
    return client_to_room.get(client, None)

def move_client_to_room(client: ServerConnection, room_id: str) -> Room:
    """
    move the given client to the room with the given room_id.
    return the Room instance that the client is moved to.
    (Note: a client can only stay in zero or one room)
    ("move" means deletion from previous room and addition to the new room, given that the client is already in a room)
    """
    old_room: Room | None = get_current_room(client)
    if old_room is not None:
        old_room.remove_client(client)

    # for a newly born client, can still get in new room
    new_room: Room = get_or_create_room(room_id)
    new_room.add_client(client)

    client_to_room[client] = new_room # update reverse mapping from client to room

    return new_room


def remove_client(client:ServerConnection) -> None:
    """
    remove the given client from its current room, if it is in any room.
    """
    room: Room | None = client_to_room.pop(client, None)

    if room is not None:
        room.remove_client(client)
    

# async connection handler ===
# =================



async def handler(websocket: ServerConnection) -> None:
    """
    for each client connection that's made to this server,
    this handler function will be called to handle the connection.
    """

    # each client will get their own instance of this handler function.
    print("A client just connected")

    # assign to default room:
    move_client_to_room(websocket, DEFAULT_ROOM)

    # get the room instance
    current_room: Room | None = get_current_room(websocket)

    if current_room is None:
        print("Error: something wrong in server handler")
        await websocket.send(json.dumps({
            "type": "error",
            "data": {"message": "server internal error: room not found, in, server handler"}
        }))
        await websocket.close(code = 1011, reason="server internal error: room not found")
        raise RuntimeError("server internal error: room not found, in, server handler")

    print(f"this lobby contains clients count: -> {len(current_room.clients)}")

    try:
        # this loop ends only when the WebSocket connection closes or an error happens. (for a particular ServerConncetion)
        async for message in websocket: # listen for messages from this client
            raw_message = message
            #
            try:
                packet: dict = json.loads(raw_message)  

            except json.JSONDecodeError:
                print("main server received something that cannot be parsed to json format", raw_message)
                # ignore the malformed message and keep listening to next possible message from this client.
                continue

            # determine packet type
            packet_type: str | None = packet.get("type")

            # ===
            # CHAT
            # ===
            if packet_type == "chat":
                # validate
                chat_packet: ChatPacket | None = parse_chat_packet(packet)

                if chat_packet is None:
                    print("[INVALID][CHAT] malformed chat packet:",
                          packet
                    )
                    continue # ignore and still listen


                # now, the data with/around packet has passed validation
                data: ChatData = chat_packet["data"]
                sender: str = data["sender"]
                chat_message: str = data["message"]
                print(f"[{time.perf_counter():.6f}][RECEIVED][CHAT][{sender}]{chat_message}")

                #find current room
                current_room = get_current_room(websocket)

                if current_room is not None:
                    # Broadcast only inside that room.
                    await current_room.broadcast(raw_message, sender=websocket)

            # ===
            # JOIN ROOM
            # ===

            elif packet_type == "join_room":
                # validate
                join_packet: JoinRoomPacket | None = parse_join_room_packet(packet)

                if join_packet is None:
                    print("[INVALID][JOIN_ROOM] malformed join_room packet:",
                          packet
                    )
                    continue # ignore and still listen

                # validation passed
                join_data: JoinRoomData = join_packet["data"]
                target_room: str = join_data["room_id"]
                player_id: str = join_data["player_id"]
                display_name: str = join_data["display_name"]

                # move client to this target room
                move_client_to_room(websocket, target_room)

                print(f"[ROOM SWITCH DONE] client [name '{display_name}' "
                      f"with id '{player_id}'] moved to room '{target_room}'")

                # notify the client that it has successfully joined the room
                room_joined_packet: RoomJoinedPacket = {
                    "type": "room_joined",
                    "data": {
                        "room_id": target_room,
                        "player_id": player_id,
                        "display_name": display_name
                    }
                }
                await websocket.send(json.dumps(room_joined_packet))

            # ===
            # UNKNOWN PACKET TYPE
            # ===
            else:
                print(f"[UNKNOWN PACKET TYPE] TYPE TO BE:", packet_type, " | RAW PACKET:", packet)

    except websockets.ConnectionClosed:
        # normal disconnect (no error) # happens when ctrl-c or crash
        pass

    except Exception as e:
        print("Unexpected error:", e)

    # when client disconnects...
    finally: # remove registered clent even if error occurs
        
        remove_client(websocket) # remove the client from its current room, if it is in any room
        print("A client disconnected from one or more rooms")



# ===
# MAIN AND SERVER ENTRY
# ===     
        



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