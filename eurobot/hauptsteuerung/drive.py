"""
This module sends waypoints to the drive. The coordinates are first checked if they are on the table.
Then redundend points are removed
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import time
import copy
import queue
import math
from libraries import can
from hauptsteuerung import route_finding


class Drive():
    def __init__(self, can_socket):
        self.can_socket = can_socket
        self.route_finder = route_finding.RouteFinding(self.can_socket)
        self.speed = 3
        self.close_range_detection = True
        self.enemy_detection = True
        self.my_robot = None
        self.my_robot_new_position = None
        self.robots = []

    def add_my_robot(self, robot):
        self.my_robot = robot
        self.route_finder.add_my_robot(robot)
        self.my_robot_new_position = self.my_robot.get_new_position_lock()

    def add_robot(self, robot):
        self.robots.append(robot)
        self.route_finder.add_robot(robot)

    def set_speed(self, speed):
        self.speed = speed

    def set_close_range_detection(self, activate):
        self.close_range_detection = activate

    def set_enemy_detection(self, activate):
        self.enemy_detection = activate

    def drive_route(self, destination, timeout=15):
        starting_time = time.time()
        arrived = False
        while arrived is False:
            route, path_len = self.route_finder.calculate_path(destination)
            arrived = self.drive_path(route, destination)
            if time.time() - starting_time > timeout:
                return False
            time.sleep(0.5)
        return True

    def drive_path(self, path, destination, path_speed=None, end_speed=None, blocking=True):
        if end_speed is None:
            end_speed = self.speed
        if path_speed is None:
            path_speed = self.speed
        x, y, angle = destination
        in_save_zone = True
        wrong_point = None
        filtered_path = copy.copy(path)
        self.filter_path(filtered_path)
        save_zone = [[300, 2700], [300, 2700]]
        for point in filtered_path:
            if save_zone[0][0] > point[0] > save_zone[0][1] or save_zone[1][0] > point[1] > save_zone[1][1]:
                in_save_zone = False
                wrong_point = point
        if save_zone[0][0] > x > save_zone[0][1] or save_zone[1][0] > y > save_zone[1][1]:
            in_save_zone = False
            wrong_point = x, y
        if in_save_zone:
            can_msg = {
                'type': can.MsgTypes.Goto_Position.value,
                'x_position': int(x),
                'y_position': int(y),
                'angle': int((abs(angle) % 360000)*100),
                'speed': end_speed,
                'path_length': len(filtered_path),
            }
            self.can_socket.send(can_msg)
            time.sleep(0.002)
            if len(filtered_path) > 0:
                for point in filtered_path:
                    can_msg = {
                        'type': can.MsgTypes.Path.value,
                        'x': point[0],
                        'y': point[1],
                        'speed': path_speed
                    }
                    self.can_socket.send(can_msg)
            if blocking:   # TODO: add timeout
                return self.wait_for_arrival(path, speed=max(path_speed, end_speed))
        else:
            can_msg = {
                'type': can.MsgTypes.Emergency_Stop.value,
                'code': 0,
            }
            self.can_socket.send(can_msg)
            raise Exception('Coordinates outside the table:' + wrong_point)
        return True

    def filter_path(self, path):
        if len(path) > 3:
            points_to_delete = []
            for i in range(len(path)-2):
                for dir in (0, 1):
                    if ((path[i][dir] == path[i+1][dir] and path[i+1][dir] == path[i+2][dir]) or
                            (path[i][0] - path[i+1][0] == path[i+1][0] - path[i+2][0]) and
                            (path[i][1] - path[i+1][1] == path[i+1][1] - path[i+2][1])):
                        points_to_delete.append(i+1)
            #print(len(path), set(points_to_delete))
            for index in reversed(sorted(list(set(points_to_delete)))):
                del path[index]

    def wait_for_arrival(self, path, speed=100):    # TODO: add timeout
        path_pointer = 0
        robot_big = self.my_robot.name == 'Roboter-gross'
        break_distance = 250 + (300 / 100 * speed)  # TODO: not tested
        drive_queue = queue.Queue()
        close_range_queue = queue.Queue()
        drive_queue_number = self.can_socket.create_queue(can.MsgTypes.Drive_Status.value, drive_queue)
        close_range_queue_number = self.can_socket.create_queue(can.MsgTypes.Close_Range_Dedection.value, close_range_queue)
        arrived = False
        emergency = False
        while arrived is False and emergency is False:
            try:
                drive_msg = drive_queue.get_nowait()
                if drive_msg['status'] == 0:
                    arrived = True
            except queue.Empty:
                pass
            if self.close_range_detection:
                try:
                    range_msg = close_range_queue.get_nowait()
                    if ((range_msg['front_middle_correct'] and range_msg['distance_front_middle'] < break_distance) or
                       (range_msg['front_left_correct'] and range_msg['distance_front_left'] < break_distance) and robot_big or
                       (range_msg['front_right_correct'] and range_msg['distance_front_right'] < break_distance)):
                        emergency = True
                        can_msg = {
                            'type': can.MsgTypes.Emergency_Stop.value,
                            'code': 0,
                        }
                        self.can_socket.send(can_msg)
                except queue.Empty:
                    pass
            if self.my_robot_new_position.acquire(False):   # TODO: Not tested
                my_position = self.my_robot.get_position()
                for i, point in enumerate(path[path_pointer:path_pointer+6]):
                    if math.sqrt((my_position[0] - point[0])**2 + (my_position[1] - point[1])**2) < 200:
                        path_pointer += (i+1)
            if self.enemy_detection:
                for robot in self.robots:
                    position = robot.get_position()
                    if position:
                        for point in path[path_pointer:path_pointer+20]:
                            if math.sqrt((position[0] - point[0])**2 + (position[1] - point[1])**2) < 200:
                                emergency = True
                                can_msg = {
                                    'type': can.MsgTypes.Emergency_Stop.value,
                                    'code': 0,
                                }
                                self.can_socket.send(can_msg)
            time.sleep(0.010)
        self.can_socket.remove_queue(close_range_queue_number)
        self.can_socket.remove_queue(drive_queue_number)
        if emergency:
            return False
        else:
            return True