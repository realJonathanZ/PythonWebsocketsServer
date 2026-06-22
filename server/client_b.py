import asyncio
import websockets


# Client B demo:
# 1) connect to the server
# 2) send one test message
# 3) keep listening for incoming messages from other clients
async def run():
    # open a persistent WebSocket connection to the Python server
    async with websockets.connect("ws://localhost:8765") as ws:

        print("Client B connected")

        # one initial message 
        await ws.send("Hello from B")

        # keep waiting for messages until the connection closes
        async for message in ws:
            print("Client B received:", message)


# entry point: start Client B's async workflow
asyncio.run(run())