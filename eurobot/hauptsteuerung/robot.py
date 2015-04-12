"""
This module contains classes that represent the state of the robot
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import time
import threading
import numpy as np


class RobotPosition():
    def __init__(self, can_socket, msg_type, size):
        self.size = size
        self.position = (0, 0)
        self.angle = 0
        self.lock = threading.Lock()
        resolution = 200
        table_size = 2000
        self.map = np.zeros((resolution*1.5, resolution))
        self.scale = table_size / resolution
        self.last_position_update = 0
        self.last_angle_update = 0
        can_socket.create_interrupt(msg_type, self.can_robot_position)

    def can_robot_position(self, can_msg):
        margin = int(20 * self.scale)
        # TODO: check sender ID (in case drive and navigation both send)
        if can_msg['position_correct']:
            x, y = can_msg['x_position'], can_msg['y_position']
            with self.lock:
                self.position = x, y
                self.map[round(x / self.scale) - margin: round(x / self.scale) + margin,
                         round(y / self.scale) - margin: round(y / self.scale) + margin] += 1
            self.last_position_update = time.time()
        if can_msg['angle_correct']:
            with self.lock:
                self.angle = can_msg['angle']
            self.last_angle_update = time.time()

    def get_position(self):
        with self.lock:
            return self.position

    def get_angle(self):
        with self.lock:
            return self.angle

    def get_map(self):
        with self.lock:
            return self.map


class PositionMyRobot(RobotPosition):
    def __init__(self, can_socket, msg_type, name, size=20):
        super().__init__(can_socket, msg_type, size)
        self.name = name


class PositionOtherRobot(RobotPosition):
    def __init__(self, can_socket, msg_type, size=20):
        super().__init__(can_socket, msg_type, size)
        self.check_thread = threading.Thread(target=self.check_navigation)
        self.check_thread.setDaemon(1)
        self.check_thread.start()

    def check_navigation(self):
        while True:
            now = time.time()
            if now - self.last_position_update > 0.1:
                self.angle = None
            if now - self.last_angle_update > 0.1:
                self.position = None
            time.sleep(0.03)