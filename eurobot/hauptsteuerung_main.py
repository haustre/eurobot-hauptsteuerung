"""
This is the main file to execute the software of the Beaglebone.
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import sys
import time
import socket
import threading
from libraries import can
from hauptsteuerung import debug


def main():
    """ Main programm running on Robot"""
    hostname = socket.gethostname()
    if not (hostname == 'Roboter-klein' or hostname == 'Roboter-gross'):
        print('Wrong Hostname\nSet Hostname to "Roboter-klein" or "Roboter-gross"')
        sys.exit(0)
    if len(sys.argv) != 2:
        print('Provide CAN device name (can0, vcan0 etc.)')
        sys.exit(0)
    can_socket = can.Can(sys.argv[1], can.MsgSender.Hauptsteuerung)
    debugger = debug.LaptopCommunication(can_socket)
    while True:
        time.sleep(1)


class Countdown():
    def __init__(self):
        """
        This class counts down the remaining time till the end of the game
        """
        self.countdown_loop = threading.Thread(target=self.run)
        self.countdown_loop.setDaemon(1)
        self.countdown_loop.start()

    def run(self):
        pass

if __name__ == "__main__":
    main()