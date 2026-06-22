import asyncio
import websockets


# Client C demo:
# 1) connect to the server
# 2) send one test message
# 3) keep listening for incoming messages from other clients
async def run():
    # open a persistent WebSocket connection to the Python server
    async with websockets.connect("ws://localhost:8765") as ws:

        print("Client C connected")

        # one initial message 
        await ws.send("Hello from C")

        # keep waiting for messages until the connection closes
        async for message in ws:
            print("Client C received:", message)


# entry point: start Client C's async workflow
asyncio.run(run())
