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
    debugger.start()
    enemy = debug.EnemySimulation(can_socket,  2, 10)
    enemy.start()
    while True:
        time.sleep(1)


class Countdown():
    def __init__(self):
        """
        This class counts down the remaining time till the end of the game
        """
        self.running = False
        self.start_time = 0
        self.game_time = 90  # Time the end of the game in seconds
        self.timers_to_start = []

    def start(self):
        self.start_time = time.time()
        self.running = True
        for timer in self.timers_to_start:
            threading.Timer(timer).start()

    def time_left(self):
        if self.running:
            time_left = int(self.game_time - (time.time() - self.start_time))
        else:
            time_left = False
        return time_left

    def set_interrupt(self, object_to_call, interrupt_name, time_left):
        if self.running:
            interrupt_time = self.game_time - time_left
            threading.Timer(interrupt_time, object_to_call.interrupt, [interrupt_name]).start()
        else:
            call = object_to_call, interrupt_name, time_left
            self.timers_to_start.append(call)

if __name__ == "__main__":
    main()