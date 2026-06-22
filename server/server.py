import asyncio
import websockets

connected_clients = set() # storing all active clients

async def handler(websocket):
    # each client will get their own instance of this handler function.
    print("A client just connected")

    connected_clients.add(websocket) # add the new client to the set
    
    try:
        # this loop ends only when the WebSocket connection closes or an error happens.
        async for message in websocket: # listen for messages from the client
        # async for: keeps waiting for the next item in the stream of the presistent WebSocket connection.
            print("Received message:", message)

            # broadcast the message to all other connected clients
            for client in connected_clients:
                if client != websocket: # don't send the message back to the sender
                    await client.send(message) # await the message is actually sent, before move on

    except websockets.ConnectionClosed:
        # normal disconnect (no error) # happens when ctrl-c or crash
        pass

    except Exception as e:
        print("Unexpected error:", e)

    # when client disconnects...
    finally: # remove registered clent even if error occurs
        connected_clients.remove(websocket)
        print("A client just disconnected")

async def main():
    server = await websockets.serve(
        handler,        # what runs when server started? # the handler function to handle incoming connections
        "localhost",    # who can connect? now: only this pc # host to listen on
        8765            # port number? # port to listen on
    )

    print("WebSocket server running on ws://localhost:8765") # ws:// is the WebSocket protocol

    await server.wait_closed() # don't exit, keep the server alive forever


asyncio.run(main()) # entry point: run the main function to start the server