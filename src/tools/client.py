import asyncio
import websockets


async def tally():
    uri = 'ws://localhost:8765'
    async with websockets.connect(uri) as websocket:
        direction = await websocket.recv()
        print(direction)

asyncio.get_event_loop().run_until_complete(tally())
