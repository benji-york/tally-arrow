import asyncio
import websockets
import time
import threading
from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse
from osc4py3 import oscmethod as osm

# Start the system.
osc_startup()

current_tally = None

def handle_program_response(address, *args):
    global current_tally
    if len(args) and args[0]:
        # This source is being sent to the program out.
        if address[-2] == '/':
            current_tally = int(address[-1])
            print('tally:', current_tally)


# Make server channels to receive packets.
osc_udp_server('192.168.0.105', 4445, 'server')
osc_method('/atem/program/*', handle_program_response, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)

osc_udp_client('192.168.0.99', 3333, 'aclientname')

msg = oscbuildparse.OSCMessage('/atem/send-status', None, [])
osc_send(msg, 'aclientname')


tally_to_arrow_angle = {
    2: -5,
    3: -20,
    4: +5,
    5: 0,
}


async def tally(websocket, path):
    print('path:', path)
    last_tally = None

    async for message in websocket:
        print('->', message)
        while current_tally == last_tally:
            await asyncio.sleep(0.001)
        angle = tally_to_arrow_angle.get(current_tally, '?')
        last_tally = current_tally
        print('<-', angle)
        await websocket.send(str(angle))
    print('exiting websocket handler')


def osc_process_forever():
    while True:
        osc_process()
        time.sleep(0.001)

osc_thread = threading.Thread(target=osc_process_forever, daemon=True)
osc_thread.start()

start_server = websockets.serve(tally, '0.0.0.0', 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

osc_terminate()
