import asyncio
import websockets
import json
from websockets.asyncio.server import ServerConnection

connected_clients: set[ServerConnection] = set() # storing all active clients


async def broadcast(sender: ServerConnection, message: str):
    """
    let the sender send one message and broadcast it out except to the sender itself.
    """

    disconnected_clients: set[ServerConnection] = set() # store disconnected clients to remove them later

    for client in list(connected_clients):
        # sender do not send message to itself..
        if client != sender:
            # send the parsed json str message out
            try:
                await client.send(message)

            except websockets.ConnectionClosed:
                # register this websocket connection as disconnected to the set.
                disconnected_clients.add(client)

    # clean up dead connections..
    for client in disconnected_clients:
        connected_clients.discard(client) # discard(): more-safe remove()


async def handler(websocket: ServerConnection):
    """
    for each client connection that's made to this server,
    this handler function will be called to handle the connection.
    """

    # each client will get their own instance of this handler function.
    print("A client just connected")
    connected_clients.add(websocket) # add the new client to the set
    print(f"connected total clients count: {len(connected_clients)}")
    
    try:
        # this loop ends only when the WebSocket connection closes or an error happens. (for a particular ServerConncetion)
        async for message in websocket: # listen for messages from this client
            # parse json and print its contents (Only for logging and debugging purpose)
            try:
                packet = json.loads(message)  # Note: debugged point: check difference with .load() and .loads()

                print(
                    f"received one message from one client, inspected as below:\n"
                    f"type={packet.get('type', 'unknown')}\n"
                    f"sender={packet.get('data', {}).get('sender', 'unknown')}"  # define quick getter mthod TODO
                    f"message={packet.get('data', {}).get('message', 'unknown')}\n"
                )

            except json.JSONDecodeError:
                print("main server received invalid json (or problem when loading):", message)

            await broadcast(websocket, message) # broadcast the message to all other clients


    except websockets.ConnectionClosed:
        # normal disconnect (no error) # happens when ctrl-c or crash
        pass

    except Exception as e:
        print("Unexpected error:", e)

    # when client disconnects...
    finally: # remove registered clent even if error occurs
        connected_clients.discard(websocket) # discard(): more-safe remove() # removing it twice for safety..
        print("A client just disconnected")
        print(f"remaining connected total clients count: {len(connected_clients)}")



async def main():
    server = await websockets.serve(
        handler,        # what runs when server started? # the handler function to handle incoming connections
        host = "localhost",    # who can connect? now: only this pc # host that listens on
        port = 8765            # port number? # port to listen on
    )

    print("WebSocket server running on ws://localhost:8765") # ws:// is the WebSocket protocol

    # await: process one message at a time for this ServerConnection instance(i.e. one client)
    await server.wait_closed() # don't exit, keep the server alive forever


asyncio.run(main()) # entry point: run the main function to start the server