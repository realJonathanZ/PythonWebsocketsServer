import asyncio
import json
import websockets
from websockets import ClientConnection 

from protocal import ChatPacket


# Client C demo:
# 1) connect to the server
# 2) send one test message
# 3) keep listening for incoming messages from other clients


async def send_loop(ws: ClientConnection, name: str) -> None:
    """
    read user input and send chat packets to the server forever.
    """
    while True:
        message = await asyncio.to_thread(input, "enter awesome message to all other clients: ")

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
        data: ChatPacket = json.loads(message)

        print("\n--- some message is received by client C ! ---")
        print("message type:", data["type"])
        print("message sender:", data["data"]["sender"])
        print("message content:", data["data"]["message"])
        print("---------------------------------------\n")


async def run() -> None:
    """
    connect client C and run send/receive loops concurrently.
    """
    # open a persistent WebSocket connection to the Python server
    async with websockets.connect("ws://localhost:8765") as ws:

        print("Client C connected")

        # run both coroutines together so 
        # sending(reading input&parse&send) and receiving(continuous listening) messages happen in parallel.
        await asyncio.gather(
            send_loop(ws, "C"),
            receive_loop(ws)
        )


# entry point: start Client C's async workflow
asyncio.run(run())
