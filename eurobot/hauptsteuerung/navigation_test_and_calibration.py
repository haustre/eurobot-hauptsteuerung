"""
This module is used for calibrating and testing the navigation system V3.0
"""
__author__ = 'Scheurer Simon'
__license__ = "GPLv3"

import time
from libraries import can





class NavigationTest:
    """ class for calibrating and testing navigation V3.0 """

    def __init__(self, can_socket):
        self.can_socket = can_socket

    def run_test(self, test_program):
        """ test chooser

        :param test_program: test or calibration program, which should run
        :return: None
        """
        # ------------------------------------------------
        # Options
        #
        # rcr = Rotation calibration clockwise
        # rcl = Rotation calibration counterclockwise
        #
        # tt1 = Total test beginning with Point 1
        # tt2 = Total test beginning with Point 2
        # tt3 = Total test beginning with Point 3
        # tt4 = Total test beginning with Point 4
        #
        # ------------------------------------------------


        # Rotation calibration ------------------------------------------------------------------- #
        if test_program == "rcr":
            self.rotation_calibration("right")


        elif test_program == "rcl":
            self.rotation_calibration("left")

        else:
            pass


    def rotation_calibration(self, turn_direction):
        """ program to calibrated angle

        :param turn_direction: direction of turning
        :return: None
        """
        # Drive to point 1
        self.drive.drive_path([], 1150, 1600, None)

        # Drive to point 2
        self.drive.drive_path([], 400, 1600, None)

        # Drive to point 3 and reference on side fence
        self.drive.drive_path([], 400, 1600, None)

        # Wait 15 seconds, that user can measure angle of robot
        time.sleep(15)

        # Drive to point 2
        self.drive.drive_path([], 400, 1600, 0)

        # Set direction
        if turn_direction == "right":
            speed_motor_left = 40
            speed_motor_right = -40
        else:
            speed_motor_left = -40
            speed_motor_right = 40

        can_msg = {
            'type': can.MsgTypes.Debug_Drive,
            'speed_left': int(speed_motor_left),
            'speed_right': int(speed_motor_right),
        }

        # Send values to RoboDrive
        self.can_socket.send(can_msg)

        # Wait until 100 turns are over
        time.sleep(100)

        # Stop robot
        can_msg = {
            'type': can.MsgTypes.Debug_Drive,
            'speed_left': int(0),
            'speed_right': int(0),
        }
        self.can_socket.send(can_msg)


