__author__ = 'mw'

from can import Can
from ethernet import Server
import time
import struct


def main():
    packer = struct.Struct('ff')
    can_id, can_mask = 0x600, 0x600
    s_debug = Can(can_id, can_mask, 'vcan0')
    tcp = Server()
    while True:
        data = s_debug.receive()
        if data:
            data = packer.unpack(data)
            tcp.write(data)
            #print(data)
        time.sleep(0.01)

main()