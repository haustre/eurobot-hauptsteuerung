"""
To test the software before the whole hardware is build this module allows to send fake position data over CAN.
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

    position_robot1 = Position(50)
    position_robot2 = Position(70)
    while True:
        x, y, angle = position_robot1.get_coordinates()
        can_msg = {
            'type': can.MsgTypes.Position_Robot_1.value,
            'position_correct': True,
            'angle_correct': False,
            'angle': angle,
            'y_position': y,
            'x_position': x
        }
        can_connection.send(can_msg)

        x, y, angle = position_robot2.get_coordinates()
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
        time.sleep(1/50)


class Position():
    def __init__(self, speed):
        self.speed = speed
        self.x = random.randrange(0, 30000)
        self.y = random.randrange(0, 15000)
        self.angle = random.randrange(0, 36000)

    def get_coordinates(self):
        self.x += self.speed
        if self.x > 30000:
            self.x = 0
        self.y += self.speed
        if self.y > 15000:
            self.y = 0
        self.angle += self.speed
        if self.angle > 36000:
            self.angle = 0
        return self.x, self.y, self.angle

if __name__ == "__main__":
    main()


