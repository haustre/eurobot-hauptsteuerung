"""
This is the main file to execute the software of the Beaglebone.
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import sys
import time
import socket
import threading
import queue
from libraries import can
from hauptsteuerung import debug
from hauptsteuerung import game_logic


def main():
    """ Main programm running on Robot"""
    hostname = socket.gethostname()
    if len(sys.argv) == 3:
        can_connection = sys.argv[1]
        hostname = sys.argv[2]
    else:
        can_connection = 'can0'
        if not (hostname == 'Roboter-klein' or hostname == 'Roboter-gross'):
            print('Wrong Hostname\nSet Hostname to "Roboter-klein" or "Roboter-gross"')
            sys.exit(0)
    can_socket = can.Can(can_connection, can.MsgSender.Hauptsteuerung)
    countdown = game_logic.Countdown(can_socket)
    debugger = debug.LaptopCommunication(can_socket)
    debugger.start()
    enemy = debug.EnemySimulation(can_socket,  3, 70)
    peripherie_queue = queue.Queue()
    can_socket.create_queue(can.MsgTypes.Peripherie_inputs.value, peripherie_queue)

    game_started = False
    while game_started is False:
        peripherie_msg = peripherie_queue.get()
        print(peripherie_msg)
        if peripherie_msg['emergency_stop'] is False and peripherie_msg['key_is_removed'] is True:
            game_started = True

    countdown.start()   # start of the game
    #enemy.start()
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()