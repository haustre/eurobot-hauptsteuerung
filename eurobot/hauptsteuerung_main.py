"""
This is the main file to execute the software of the Beaglebone.
"""
__author__ = 'Würsch Marcel'
__license__ = "GPLv3"

import sys
import time
from libraries import can
from hauptsteuerung import debug


def main():
    """ Main programm running on Robot"""
    if len(sys.argv) != 2:
        print('Provide CAN device name (can0, vcan0 etc.)')
        sys.exit(0)
    can_socket = can.Can(sys.argv[1], can.MsgSender.Hauptsteuerung)
    debugger = debug.LaptopCommunication(can_socket)
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()