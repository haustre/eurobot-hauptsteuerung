"""
This module is used for calibrating and testing the navigation system V3.0
"""
__author__ = 'Scheurer Simon'
__license__ = "GPLv3"

import time
from libraries import can


class NavigationTest:
    """ class for calibrating and testing navigation V3.0 """

    def __init__(self, can_socket, drive):
        self.can_socket = can_socket
        self.drive = drive

        self.system_test_points = [{'Position': (367, 944), 'Side': 'Left'},     # Start Position
                                   {'Position': (350, 350), 'Side': 'Left'},     #P1
                                   {'Position': (2650, 350), 'Side': 'Right'},   #P2
                                   {'Position': (2650, 1650), 'Side': 'Right'},  #P3
                                   {'Position': (350, 1650), 'Side': 'Left'},    #P4
                                   {'Position': (1000, 1000), 'Side': 'Left'},   #P5
                                   {'Position': (2000, 1000), 'Side': 'Right'}]  #P6


    def run_test(self, test_program, number, speed):
        """ test chooser

        :param test_program: test or calibration program, which should run
        :param number: number of turns or repeats (1-100)
        :param speed: speed of driving (10-100)
        :return: None
        """
        # ------------------------------------------------
        # Options
        #
        # test_programm:
        # rtr = Rotation test clockwise (right)
        # rtl = Rotation test counterclockwise (left)
        # st1 = System test beginning with Point 1
        # st2 = System test beginning with Point 2
        # st3 = System test beginning with Point 3
        # st4 = System test beginning with Point 4
        #
        # number:
        # number of turns or repeats (1-100)
        #
        # speed:
        # speed of driving (10-100)
        #
        # ------------------------------------------------


        # Print test parameters out
        print("===========================")
        print("Following test drive starts")
        print("===========================")
        print(" ")
        print("Testname: ", test_program)
        print(" ")
        print("Number of repeats: ", number)
        print(" ")
        print("Drive speed: ", speed, "%")
        print(" ")
        print("===========================")

        # Rotation test ------------------------------------------------------------------- #
        if test_program == "rtr":
            self.rotation_test("right", number, speed)

        elif test_program == "rtl":
            self.rotation_test("left", number, speed)

        # System test --------------------------------------------------------------------- #
        elif test_program == "st1":
            self.system_test(1, number, speed)

        elif test_program == "st2":
            self.system_test(2, number, speed)

        elif test_program == "st3":
            self.system_test(3, number, speed)

        elif test_program == "st4":
            self.system_test(4, number, speed)

        # Other --------------------------------------------------------------------------- #
        else:
            print("Test do not exist!!!!!")
            pass


    def rotation_test(self, turn_direction, number, speed):
        """ program to calibrate and test angle

        :param turn_direction: direction of turning
        :param number: number of turns or repeats (1-100)
        :param speed: speed of driving (10-100)
        :return: None
        """
        # Set speed
        self.drive.set_speed(speed)

        # Drive to point 1
        self.drive.drive_path([], (1150, 1600), None, end_speed=40)

        # Drive to point 2
        self.drive.drive_path([], (400, 1600), None, end_speed=-40)

        # Drive to point 3 and reference on side fence
        self.drive.drive_path([], (100, 1600), None, end_speed=-10)

        # Wait 15 seconds, that user can measure angle of robot
        time.sleep(15)

        # Drive to point 2
        self.drive.drive_path([], (400, 1600), 0, end_speed=40)

        # Set direction
        if turn_direction == "right":
            speed_motor_left = speed
            speed_motor_right = -speed
        else:
            speed_motor_left = -speed
            speed_motor_right = speed

        can_msg = {
            'type': can.MsgTypes.Debug_Drive.value,
            'speed_left': int(speed_motor_left),
            'speed_right': int(speed_motor_right)
        }

        # Take start time
        start_time = time.time()

        # Send values to RoboDrive
        self.can_socket.send(can_msg)

        # Wait until number of turns are over
        waitTime = 0.7808 * 100 / speed * number
        time.sleep(waitTime)

        # Stop robot
        can_msg = {
            'type': can.MsgTypes.Debug_Drive.value,
            'speed_left': int(0),
            'speed_right': int(0)
        }
        self.can_socket.send(can_msg)

        # Calculate rotation time
        deltaTime = time.time() - start_time

        print("Rotation test is finished")
        print("=========================")
        print(" ")
        print("Rotation time: ", int(deltaTime), "s")
        print("Number of rotation: ", number)
        print(" ")
        print("=========================")


    def system_test(self, first_point, numberOfPoints, speed):
        """ program to test the whole navigation system

        :param first_point: first point, where the robot drive
        :param numberOfPoints: number repeats (1-100)
        :param speed: speed of driving (10-100)
        :return: None
        """
        PointsLeft = numberOfPoints
        lastDrivenPoint = 5
        pointToDrive = first_point

        # Set speed
        self.drive.set_speed(speed)

        # Take start time
        start_time = time.time()

        # Go to first point
        self.drive.drive_path([], self.system_test_points[5]['Position'], None)
        PointsLeft -= 1

        while PointsLeft > 0:
            # Was the last point on the left side and the next point is on the right, then go to point 6 first
            if self.system_test_points[pointToDrive]['Side'] == 'Right' and self.system_test_points[lastDrivenPoint][
                    'Side'] == 'Left':
                driveFinished = self.drive.drive_path([], self.system_test_points[6]['Position'], None)
                PointsLeft -= 1
                if PointsLeft <= 0 or driveFinished is False:
                    break

            # Was the last point on the right side and the next point is on the left, then go to point 5 first
            if self.system_test_points[pointToDrive]['Side'] == 'Left' and self.system_test_points[lastDrivenPoint][
                    'Side'] == 'Right':
                driveFinished = self.drive.drive_path([], self.system_test_points[5]['Position'], None)
                PointsLeft -= 1
                if PointsLeft <= 0 or driveFinished is False:
                    break

            # Drive to the point
            driveFinished = self.drive.drive_path([], self.system_test_points[pointToDrive]['Position'], None)
            PointsLeft -= 1
            if PointsLeft <= 0 or driveFinished is False:
                break

            # Drive to the middle point
            if self.system_test_points[pointToDrive]['Side'] == 'Left':
                driveFinished = self.drive.drive_path([], self.system_test_points[5]['Position'], None, end_speed=-speed)
            else:
                driveFinished = self.drive.drive_path([], self.system_test_points[6]['Position'], None, end_speed=-speed)
            PointsLeft -= 1
            if PointsLeft <= 0 or driveFinished is False:
                break

            # Remark the last driven point
            lastDrivenPoint = pointToDrive

            # Define next point
            pointToDrive += 1
            if pointToDrive > 4:
                pointToDrive -= 4

        # Calculate drive time
        deltaTime = time.time() - start_time

        # System test is finished
        print("System test is finished")
        print("=======================")
        print(" ")
        print("First point: ", first_point)
        print("Driven points: ", numberOfPoints - PointsLeft)
        print("Number of points left: ", PointsLeft)
        print("Drive time: ", int(deltaTime), "s")
        print(" ")
        print("=======================")


