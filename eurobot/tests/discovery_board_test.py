"""
Sends CAN messages to the discovery board and checks the response
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import sys
import time
import random
from eurobot.libraries import can


def main():
    """ This function generates CAN test traffic. """
    if len(sys.argv) != 2:
            print('Provide CAN device name (can0, vcan0 etc.)')
            sys.exit(0)
    can_connection = can.Can(sys.argv[1], can.MsgSender.Debugging)
    while True:
        

        time.sleep(5)


if __name__ == "__main__":
    main()