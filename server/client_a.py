import asyncio
import json
import websockets


# Client A demo:
# 1) connect to the server
# 2) send one test message
# 3) keep listening for incoming messages from other clients
async def run():
    # open a persistent WebSocket connection to the Python server
    async with websockets.connect("ws://localhost:8765") as ws:

        print("Client A connected")

        # one initial dictionary carrying data

        packet = {
            "type": "chat",
            "data": {
                "sender": "A",
                "message": "Hello"
            }
        }

        json_str = json.dumps(packet)  # message dict to str
        
        await ws.send(json_str) # send parsed message to the server

        # keep waiting for messages until the connection closes
        async for message in ws:
            print("Client A received:", message)


# entry point: start Client A's async workflow
asyncio.run(run())