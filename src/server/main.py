import asyncio
import socket
import struct
import time
import websockets


HEADER_SIZE = 12

SYNC = 1
CONNECT = 2
ACK = 16


class Atem:
    current_tally = None

    def __init__(self, socket_, switcher_ip):
        # Set up socket.
        self.socket = socket_
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setblocking(0)

        self.target_switcher = (switcher_ip, 9910)

    def connect(self):
        print('connecting')
        request = self.make_header(CONNECT, 8, 0x4259, 0)
        request += struct.pack('!I', 0x01000000)
        request += struct.pack('!I', 0x00)
        bytes_remaining = len(request)
        while bytes_remaining > 0:
            bytes_sent = self.socket.sendto(request, self.target_switcher)
            bytes_remaining -= bytes_sent

    def handle_packet(self, packet):
        print('processing packet')
        header = self.parse_header(packet)

        if header['kind'] & SYNC:
            self.parse(packet)

        response = self.make_header(ACK, 0, header['uid'], header['packet_id'])
        self.socket.sendto(response, self.target_switcher)

    def make_header(self, kind, packet_size, uid, ackId):
        header = b''
        header += struct.pack('!H', (kind << 11) | (packet_size + HEADER_SIZE))
        header += struct.pack('!H', uid)
        header += struct.pack('!H', ackId)
        header += struct.pack('!I', 0)
        header += struct.pack('!H', 0)
        return header

    def parse_header(self, data):
        assert len(data) >= HEADER_SIZE
        header = {}
        header['kind'] = struct.unpack('B', data[0:1])[0] >> 3
        header['size'] = struct.unpack('!H', data[0:2])[0] & 0x07FF
        header['uid'] = struct.unpack('!H', data[2:4])[0]
        header['ackId'] = struct.unpack('!H', data[4:6])[0]
        header['packet_id'] = struct.unpack('!H', data[10:12])[0]
        return header

    def parse(self, data):
        # Strip off the header, which we don't need here.
        data = data[HEADER_SIZE:]
        while len(data) > 0:
            size = struct.unpack('!H', data[0:2])[0]
            packet = data[0:size]
            data = data[size:]

            report_type = packet[4:8]
            payload = packet[8:]

            # If the report is about the program bus changing, record the new
            # tally info.
            if report_type == b'PrgI':
                self.current_tally = payload[-1]

    def do_work(self):
        while True:
            try:
                packet, _ = self.socket.recvfrom(99999)
            except BlockingIOError:
                time.sleep(0.01)
            else:
                break
        self.handle_packet(packet)


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', 9911))
atem = Atem(s, switcher_ip='192.168.1.240')
atem.connect()

tally_to_arrow_angle = {
    1: 0,
    2: -5,
    3: -20,
    4: +5,
}


async def tally(websocket, path):
    last_tally = None

    while True:
        atem.do_work()
        if atem.current_tally != last_tally:
            angle = tally_to_arrow_angle.get(atem.current_tally, '?')
            last_tally = atem.current_tally
            while True:
                try:
                    print(angle)
                    await websocket.send(str(angle))
                except websockets.exceptions.ConnectionClosedError:
                    pass
                else:
                    break

start_server = websockets.serve(tally, '0.0.0.0', 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
