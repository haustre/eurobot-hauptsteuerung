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
    can_rcv = can.Can(sys.argv[1])
    tcp = Server()
    while True:
        can_msg = can_rcv.queue_debugg.get()
        tcp.write(can_msg)
main()