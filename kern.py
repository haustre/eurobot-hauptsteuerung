__author__ = 'mw'

from can import Can
from ethernet import Server
import time
import struct
import sys


def main():
    if len(sys.argv) != 2:
       print('Provide CAN device name (can0, vcan0 etc.)')
       sys.exit(0)
    packer = struct.Struct('ff')
    can_id, can_mask = 0x600, 0x600
    s_debug = Can(can_id, can_mask, sys.argv[1])
    tcp = Server()
    while True:
        data = s_debug.receive_all()
        if data:
            for line in data:
                tcp.write(packer.unpack(line))
        time.sleep(0.01)

main()