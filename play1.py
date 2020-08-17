import time
from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse

# Start the system.
osc_startup()

from osc4py3 import oscmethod as osm


current_source = None

def handlerfunction(address, *args):
    global current_source
    if len(args) and args[0]:
        print('here')
        # This source is being sent to the program out.
        if address[-2] == '/':
            current_source = address[-1]


# Make server channels to receive packets.
osc_udp_server('192.168.0.105', 4444, 'server')
osc_method('/atem/program/*', handlerfunction, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)

osc_udp_client('192.168.0.99', 3333, 'aclientname')

# Build a simple message and send it.
#msg = oscbuildparse.OSCMessage('/atem/transition/cut', None, [])
#osc_send(msg, 'aclientname')
msg = oscbuildparse.OSCMessage('/atem/send-status', None, [])
osc_send(msg, 'aclientname')


while True:
    osc_process()
    print(current_source)

osc_terminate()
