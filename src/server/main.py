import asyncio
import random
import time
import websockets


async def tally(websocket, path):
    while True:
        await websocket.send(random.choice('1234'))
        time.sleep(1)


start_server = websockets.serve(tally, '127.0.0.1', 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
