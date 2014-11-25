__author__ = 'mw'

import sys
import can
import time


def main():
    if len(sys.argv) != 2:
            print('Provide CAN device name (can0, vcan0 etc.)')
            sys.exit(0)
    can_connection = can.Can(sys.argv[1], can.MsgSender.Debugging)

    x = 0
    y = 0
    angle = 0
    while True:
        angle += 1
        x += 1
        y += 1
        can_msg = {
            'type': can.MsgTypes.Position_Robot_1,
            'position_correct': True,
            'angle_correct': False,
            'angle': angle,
            'y_position': y,
            'x_position': x
        }
        can_connection.send(can_msg)

        can_msg = {
            'type': can.MsgTypes.Position_Enemy_1,
            'position_correct': False,
            'angle_correct': True,
            'angle': angle + 100,
            'y_position': y + 100,
            'x_position': x + 100
        }
        can_connection.send(can_msg)

        time.sleep(1/100)

main()


