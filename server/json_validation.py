# This script provides validation functions that can be called anytime before a particular
# json packet (loaded) being indexed in to retrieve info.
# So called - our last format/data type validation before json info enter production logic.
#



from typing import Any

from protocal import JoinRoomPacket, ChatPacket

def parse_join_room_packet(packet: Any) -> JoinRoomPacket | None:
    """
    Validate whether 'packet' has the expected structure of a 
    JoinRoomPacket (which is itself defined in protocal.py)

    parameter packet: the "thing" that's about to be checked. Normally, if valid, 
    it should be a python dictionary with particular structure defined in protocal.py.

    Returns: 
        JoinRoomPacket if valid, None otherwise.
    """ 
    #1: The packet itself must be python dictionary
    if not isinstance(packet, dict):
        return None

    #2: The packet must have type == "join_room"
    if packet.get("type") != "join_room":
        return None

    #3: "data" must exist and must be a dictionary
    data = packet.get("data")

    if not isinstance(data, dict):  # for a normal json expected format, the static type description of data before run-time is TypedDict..
                                    # but at runtime it is still dict
        return None

    #4 "room_id" must exists and must be a string
    room_id = data.get("room_id")

    if not isinstance(room_id,str): # same, "Literal" when static type description, str when runtime..
        return None

    #5 TODO any modification to protocal should be reflected here, for adding more rules
    
    #6 checked fine packet, return
    return packet

def parse_chat_packet(packet: Any) -> ChatPacket | None:
    """
    Validate whether 'packet' has the expected structure of a 
    ChatPacket (which is itself defined in protocal.py)

    parameter packet: the "thing" that's about to be checked. Normally, if valid, 
    it should be a python dictionary with particular structure defined in protocal.py.

    Returns: 
        ChatPacket if valid, None otherwise.
    """ 
    #1: The packet itself must be python dictionary
    if not isinstance(packet, dict):
        return None

    #2: The packet must have type == "chat"
    if packet.get("type") != "chat":
        return None

    #3: "data" must exist and must be a dictionary
    data = packet.get("data")

    if not isinstance(data, dict):  
        return None

    #4 "sender" must exists and must be a string
    sender = data.get("sender")

    if not isinstance(sender,str): 
        return None

    #5 "message" must exists and must be a string
    message = data.get("message")

    if not isinstance(message,str): 
        return None

    #6 TODO any modification to protocal should be reflected here, for adding more rules
    
    #7 checked fine packet, return
    return packet
