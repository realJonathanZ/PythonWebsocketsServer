# This file contains coder-friendly customized protocal class.
# Planning to have more protocals than just chat.

# dreaming about: "put X/O (for tictactoe)"
# "UnitMove".. "UnitAttack" .. "UnitSpawn" .. and so on (for war chess)

from typing import TypedDict, Literal


# ==== Chat protocal related section ====

# for a self-defined chat json source json, an example:
#{
#   "type": "chat",
#   "data": {
#       "sender": "A",
#       "message": "Hello I'm A."
#   }
#}

class ChatData(TypedDict):
    sender: str
    message: str

class ChatPacket(TypedDict):
    type: Literal["chat"]
    data: ChatData

# ==== join_room protocal related section ====

# for a self-defined join json source, an example:
#{
#   "type": "join_room", 
#   "data": {
#       "room_id": "24123",
#       "player_id": "18887776655",
#       "display_name": "B's Display Name"
#   }
#}

class JoinRoomData(TypedDict):
    room_id: str
    player_id: str
    display_name: str

class JoinRoomPacket(TypedDict):
    type: Literal["join_room"]
    data: JoinRoomData

# ==== room_joined protocal related section ====

# an example:
#{
#   "type": "room_joined", 
#   "data": {
#       "room_id": "24123",
#       "player_id": "18887776655",
#       "display_name": "B's Display Name"
#   }
#}


class RoomJoinedData(TypedDict):
    room_id: str
    player_id: str
    display_name: str

class RoomJoinedPacket(TypedDict):
    type: Literal["room_joined"]
    data: RoomJoinedData


# ==== PutXO protocal related section ? ====