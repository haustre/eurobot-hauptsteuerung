from eurobot.libraries import can

__author__ = 'mw'

import sys

from eurobot.libraries.ethernet import Server


def main():
    """ Main programm running on Robot"""
    if len(sys.argv) != 2:
        print('Provide CAN device name (can0, vcan0 etc.)')
        sys.exit(0)
    can_rcv = can.Can(sys.argv[1], can.MsgSender.Hauptsteuerung)
    tcp = Server()
    while True:
        can_msg = can_rcv.queue_debug.get()
        tcp.write(can_msg)

if __name__ == "__main__":
    main()