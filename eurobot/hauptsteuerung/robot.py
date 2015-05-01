"""
This module contains classes that hold the position information of the robots
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import time
import threading
import numpy as np


class RobotPosition():
    """ parent class for PositionMyRobot and PositionOtherRobot
        The objects of this class wait for position information over CAN and save them.
        They also draw a map where the robot has been on the table.
    """
    def __init__(self, can_socket, msg_type, size):
        self.size = size
        self.position = (0, 0)
        self.angle = 0
        self.lock = threading.Lock()
        resolution = 200
        table_size = 2000
        self.map = np.zeros((resolution*1.5+1, resolution+1))
        self.scale = table_size / resolution
        self.last_position_update = 0
        self.last_angle_update = 0
        self.new_position_data = []
        can_socket.create_interrupt(msg_type, self.can_robot_position)

    def get_new_position_lock(self):
        """ returns a lock which gets released each time new position information is received.

        :return: lock
        """
        lock = threading.Lock()
        self.new_position_data.append(lock)
        return lock

    def can_robot_position(self, can_msg):
        """ waits for new position information, saves them and puts them in the map """
        margin = int(200 / self.scale)  # minimum distance to an object
        # TODO: check sender ID (in case drive and navigation both send)
        if can_msg['position_correct']:
            x, y = can_msg['x_position'], can_msg['y_position']
            with self.lock:
                self.position = x, y
                self.map[round(x / self.scale) - margin: round(x / self.scale) + margin,
                         round(y / self.scale) - margin: round(y / self.scale) + margin] += 1
                for lock in self.new_position_data:  # release all locks
                    lock.acquire(False)
                    lock.release()
            self.last_position_update = time.time()
        if can_msg['angle_correct']:
            with self.lock:
                self.angle = can_msg['angle']
            self.last_angle_update = time.time()

    def get_position(self):
        """
        :return: position of the robot (x, y)
        """
        with self.lock:
            return self.position

    def get_angle(self):
        """
        :return: angle of the robot
        """
        with self.lock:
            return self.angle

    def get_map(self):
        """
        :return: map where the robot has been
        """
        with self.lock:
            return self.map


class PositionMyRobot(RobotPosition):
    """ Holds the position information of the robot on which the program is running. """
    def __init__(self, can_socket, msg_type, name, size=20):
        super().__init__(can_socket, msg_type, size)
        self.name = name


class PositionOtherRobot(RobotPosition):
    """ Holds the position information of all other robots. """
    def __init__(self, can_socket, msg_type, size=20):
        super().__init__(can_socket, msg_type, size)
        self.check_thread = threading.Thread(target=self.check_navigation)
        self.check_thread.setDaemon(1)
        self.check_thread.start()

    def check_navigation(self):
        """ checks if the position information of the navigation system is to old """
        while True:
            now = time.time()
            if now - self.last_position_update > 0.5:
                self.angle = None
            if now - self.last_angle_update > 0.5:
                self.position = None
            time.sleep(0.5)    # TODO: set correct time