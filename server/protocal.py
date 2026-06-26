# This file contains coder-friendly customized protocal class.
# Planning to have more protocals than just chat.

# dreaming about: "put X/O (for tictactoe)"
# "UnitMove".. "UnitAttack" .. "UnitSpawn" .. and so on (for war chess)

from typing import TypedDict, Literal


# ==== Chat protocal related section ====

class ChatData(TypedDict):
    sender: str
    message: str

class ChatPacket(TypedDict):
    type: Literal["chat"]
    data: ChatData

# ==== PutXO protocal related section ? ====