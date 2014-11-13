__author__ = 'mw'

import can
from ethernet import Server
import time
import struct
import sys


def main():
    if len(sys.argv) != 2:
       print('Provide CAN device name (can0, vcan0 etc.)')
       sys.exit(0)
    packer = struct.Struct('ff')
    can_rcv = can.Can(sys.argv[1])
    tcp = Server()
    while True:
        can_id, can_msg = can_rcv.queue_debugg.get()
        x, y = packer.unpack(can_msg)
        tcp_msg =(can_id, x, y)
        print(tcp_msg)
        tcp.write(tcp_msg)
main()