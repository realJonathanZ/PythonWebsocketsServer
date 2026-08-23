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
#       "room_id": "24123"
#   }
#}

class JoinRoomData(TypedDict):
    room_id: str

class JoinRoomPacket(TypedDict):
    type: Literal["join_room"]
    data: JoinRoomData



# ==== PutXO protocal related section ? ====