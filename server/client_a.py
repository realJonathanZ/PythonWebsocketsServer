import asyncio
import json
import websockets
from websockets import ClientConnection

from protocal import ChatPacket

# Client A demo:
# 1) connect to the server
# 2) send one test message
# 3) keep listening for incoming messages from other clients


async def send_loop(ws: ClientConnection, name: str) -> None:
    """
    read user input and send either chat or join_room packet to the server forever.
    """
    while True:
        # dirrectly using input() in an async function will block the event loop, so use asyncio.to_thread to run it in a separate thread.
        message = await asyncio.to_thread(input, 
                                          "enter awesome message or \"/join <room_id>\": "
                                          )
        
        if message.startswith("/join "):
            this_room_id = message[6:].strip()
            packet = {
                "type": "join_room",
                "data": {
                    "room_id": this_room_id,
                    "client_name": name
                }
            }

        else:
            packet: ChatPacket = {
                "type": "chat",
                "data": {
                    "sender": name,
                    "message": message
                }
            }

        await ws.send(json.dumps(packet))  # send parsed message to the server


async def receive_loop(ws: ClientConnection) -> None:
    """
    continuously listening for incoming broadcasted messages from
    main server and print them for this client.
    """
    # keep waiting for messages until the connection closes
    async for message in ws:
        packet: ChatPacket = json.loads(message)

        packet_type: str | None = packet.get("type")

        if packet_type == "chat":
            print("\n--- some message is received by client A ! ---")
            print("message type:", packet["type"])
            print("message sender:", packet["data"]["sender"])
            print("message content:", packet["data"]["message"])
            print("---------------------------------------\n")
            
        elif packet_type == "room_joined":
            print("\n--- client A successfully joined a room ! ---")
            print("message type:", packet["type"])
            print("room id:", packet["data"]["room_id"])
            print("client name:", packet["data"]["client_name"])
            print("---------------------------------------\n")

        else:
            print("\n--- client A received an unknown packet type ! ---")
            print("message type:", packet_type)
            print("raw packet:", packet)
            print("---------------------------------------\n")

        



async def run() -> None:
    """
    connect client A and run send/receive loops concurrently.
    """
    # open a persistent WebSocket connection to the Python server
    async with websockets.connect("ws://localhost:8765") as ws:

        print("Client A connected")

        # run both coroutines together so 
        # sending(reading input&parse&send) and receiving(continuous listening) messages happen in parallel.
        await asyncio.gather(
            send_loop(ws, "A"),
            receive_loop(ws)
        )


# entry point: start Client A's async workflow
asyncio.run(run())