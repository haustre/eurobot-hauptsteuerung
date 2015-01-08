"""
To test the software before the whole hardware is build this module allows to send fake position data over CAN.
"""
__author__ = 'Würsch Marcel'
__license__ = "GPLv3"

import sys
import time
from eurobot.libraries import can


def main():
    """ This function generates CAN test traffic. """
    if len(sys.argv) != 2:
            print('Provide CAN device name (can0, vcan0 etc.)')
            sys.exit(0)
    can_connection = can.Can(sys.argv[1], can.MsgSender.Debugging)

    x = 0
    y = 0
    angle = 0
    while True:
        angle += 10
        x += 5
        y += 5
        can_msg = {
            'type': can.MsgTypes.Position_Robot_1.value,
            'position_correct': True,
            'angle_correct': False,
            'angle': angle,
            'y_position': y,
            'x_position': x
        }
        can_connection.send(can_msg)

        can_msg = {
            'type': can.MsgTypes.Position_Enemy_1.value,
            'position_correct': False,
            'angle_correct': True,
            'angle': angle + 100,
            'y_position': y + 100,
            'x_position': x + 100
        }
        print(can_msg)
        can_connection.send(can_msg)
        print(angle)
        time.sleep(1/50)

if __name__ == "__main__":
    main()


