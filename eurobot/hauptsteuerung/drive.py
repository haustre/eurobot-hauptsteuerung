"""
This module sends waypoints to the drive. The coordinates are first checked if they are on the table.
Then redundend points are removed.
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import time
import copy
import queue
import math
from shapely.geometry import LineString, Point
from libraries import can
from hauptsteuerung import route_finding


class Drive():
    """ class for controlling the drive """
    def __init__(self, can_socket):
        self.can_socket = can_socket
        self.route_finder = route_finding.RouteFinding(self.can_socket)
        self.speed = 3
        self.close_range_detection = True
        self.enemy_detection = True
        self.my_robot = None
        self.my_robot_new_position = None
        self.robots = []
        self.rotation_direction = None
        self.stop = False
        self.running = True
        self.offset = [0, 0]

    def add_my_robot(self, robot):
        """ adds a reference to the robot

        :param robot: robot where tho program is running on
        :return: None
        """
        self.my_robot = robot
        self.route_finder.add_my_robot(robot)
        self.my_robot_new_position = self.my_robot.get_new_position_lock()

    def add_robot(self, robot):
        """ adds a reference to the robot

        :param robot: robot
        :return: None
        """
        self.robots.append(robot)
        self.route_finder.add_robot(robot)

    def set_speed(self, speed):
        """ sets the standard speed of the drive

        :param speed: speed in %
        :return: None
        """
        self.speed = speed

    def set_close_range_detection(self, activate):
        """ activates detection of enemies with the close range detection.

        :param activate: True or False
        :return: None
        """
        self.close_range_detection = activate

    def set_enemy_detection(self, activate):
        """ activates detection of enemies with the data of the navigation system.

        :param activate: True or False
        :return: None
        """
        self.enemy_detection = activate

    def turn_off(self):
        """ deactivate the drive at game end """
        self.running = False

    def set_offset_x(self, x):
        self.offset[0] = x

    def set_offset_y(self, y):
        self.offset[1] = y

    def drive_route(self, destination, angle, timeout=15):
        """ drives to a given location

        :param destination: destination (x, y) or (x, y, angle)
        :param angle: final angle
        :param timeout: timeout if point is not reachable
        :return: destination reached
        :rtype: bool
        """
        if destination is None and angle is None:
            return True
        starting_time = time.time()
        while self.stop is False:
            route, path_len = self.route_finder.calculate_path(destination)
            print(path_len)
            if path_len >= 100:  # TODO: Not tested
                #return False
                pass
            arrived = self.drive_path(route, destination, angle)
            if arrived:
                return True
            else:
                starting_time += 2  # TODO: Not tested
            time.sleep(0.5)
            if time.time() - starting_time > timeout:
                return False

    def request_stop(self):
        """ stops the robot

        :return: None
        """
        self.stop = True    # TODO: check variable in wait_for_arrival
        can_msg = {
            'type': can.MsgTypes.Emergency_Stop.value,
            'code': 0,
        }
        self.can_socket.send(can_msg)
        time.sleep(0.2)
        self.stop = False

    def drive_path(self, path, destination, angle_in, path_speed=None, end_speed=None, blocking=True, filter_path=False):
        """ drives a path to a point if the coordinates are outside the table an exception is raised

        :param path: waypoints
        :param destination: (x, y) or (x, y, angle)
        :param angle_in: final angle ( overrides the angle of destination)
        :param path_speed: speed on the path in %
        :param end_speed: speed at the end of the path in %
        :param blocking: True = wait for arrival, False = don't wait
        :return: destination reached
        :rtype: bool
        """
        if self.running:
            if destination is None and angle_in is None:
                return True
            if destination:
                if len(destination) == 2:
                    x, y = destination
                    angle = None
                elif len(destination) == 3:
                    x, y, angle = destination
                else:
                    raise Exception('Destination formatted wrong')
                x, y = int(x), int(y)
            else:
                x, y = 65535, 65535
            if angle_in is not None:
                angle = int((abs(angle_in) % 360)*100)
            elif angle is not None:
                angle = int((abs(angle) % 360)*100)
            else:
                angle = 65535
            if end_speed is None:
                end_speed = self.speed
            if path_speed is None:
                path_speed = self.speed
            in_save_zone = True
            wrong_point = None
            filtered_path = copy.copy(path)
            if filter_path:
                self.filter_path(filtered_path)
                self.filter_path2(filtered_path)
                self.filter_path3(filtered_path, 7)
            save_zone = [[99, 2901], [99, 2901]]
            for point in filtered_path:  # checks if all waypoints are on the table
                if save_zone[0][0] > point[0] > save_zone[0][1] or save_zone[1][0] > point[1] > save_zone[1][1]:
                    in_save_zone = False
                    wrong_point = point
            if save_zone[0][0] > x > save_zone[0][1] or save_zone[1][0] > y > save_zone[1][1]:
                in_save_zone = False
                wrong_point = x, y
            if in_save_zone or x == 65535 and y == 65535:
                if len(path) > 0 and path_speed > 0:  # wait for first rotation to finish.
                    my_x, my_y = self.my_robot.get_position()
                    path_x, path_y = path[0]
                    dx, dy = path_x - my_x, path_y - my_y
                    rotate_angle = math.atan2(dy, dx) / (2 * math.pi) * 360
                    rotate_angle = int((rotate_angle % 360)*100)
                    if abs(angle - rotate_angle) > 20 * 100:
                        can_msg = {
                            'type': can.MsgTypes.Goto_Position.value,
                            'x_position': 65535,
                            'y_position': 65535,
                            'angle': rotate_angle,
                            'speed': int(self.speed),
                            'path_length': 0,
                        }
                        drive_queue = queue.Queue()
                        drive_queue_number = self.can_socket.create_queue(can.MsgTypes.Drive_Status.value, drive_queue)
                        self.can_socket.send(can_msg)
                        try:
                            drive_msg = drive_queue.get(timeout=3)
                        except queue.Empty:
                            print("Drive rotation timed out")
                        self.can_socket.remove_queue(drive_queue_number)
                can_msg = {
                    'type': can.MsgTypes.Goto_Position.value,
                    'x_position': x - self.offset[0],
                    'y_position': y - self.offset[1],
                    'angle': angle,
                    'speed': end_speed,
                    'path_length': len(filtered_path),
                }
                self.can_socket.send(can_msg)
                time.sleep(0.002)   # necessary because software on the drive board is slow
                if len(filtered_path) > 0:
                    for point in filtered_path:
                        can_msg = {
                            'type': can.MsgTypes.Path.value,
                            'x': point[0] - self.offset[0],
                            'y': point[1] - self.offset[1],
                            'speed': path_speed
                        }
                        self.can_socket.send(can_msg)
                if blocking:   # TODO: add timeout
                    return self.wait_for_arrival(speed=max(path_speed, end_speed))
            else:
                can_msg = {
                    'type': can.MsgTypes.Emergency_Stop.value,
                    'code': 0,
                }
                self.can_socket.send(can_msg)
                raise Exception('Coordinates outside the table:' + str(wrong_point[0]) + str(wrong_point[1]))
            return True

    def filter_path(self, path):
        """ filters a path to cause less CAN traffic

        :param path: path to filter
        :return: None
        """
        if len(path) > 3:
            points_to_delete = []
            for i in range(len(path)-2):
                for dir in (0, 1):
                    if ((path[i][dir] == path[i+1][dir] and path[i+1][dir] == path[i+2][dir]) or
                            (path[i][0] - path[i+1][0] == path[i+1][0] - path[i+2][0]) and
                            (path[i][1] - path[i+1][1] == path[i+1][1] - path[i+2][1])):
                        points_to_delete.append(i+1)
            for index in reversed(sorted(list(set(points_to_delete)))):
                del path[index]

    def filter_path2(self, path):
        points_to_delete = []
        for i in range(len(path)-1):
            if abs(path[i][0] - path[i+1][0]) <= 1 and abs(path[i][1] - path[i+1][1]) <= 5:
                points_to_delete.append(i+1)
        for index in reversed(sorted(list(set(points_to_delete)))):
            del path[index]

    def filter_path3(self, path, max_error):
        points_to_delete = []
        i = 0
        while i < len(path)-2:
            line = LineString([path[i], path[i+2]])
            point = Point(path[i+1])
            distance_from_line = point.distance(line)
            if distance_from_line <= max_error:
                points_to_delete.append(i+1)
                i += 2
            else:
                i += 1
        for index in reversed(sorted(list(set(points_to_delete)))):
            del path[index]

    def wait_for_arrival(self, speed=100):    # TODO: add timeout
        """ controls if the drive is free and breaks if a robot is in the way

        :param path: path to check for other robots
        :param speed: speed for calculating the close range detection
        :return: destination reached
        :rtype: bool
        """
        x_min, x_max = 150, 2850
        y_min, y_max = 150, 1850
        stair_x = (967 - 15, 2033 + 15)
        stair_y = (0, 580 + 15)
        robot_big = self.my_robot.name == 'Roboter-gross'
        if robot_big:
            break_distance = 250 + (300 / 100 * speed)  # TODO: not tested
            sensor_min = 150
            sensors = ['distance_front_middle', 'distance_front_left', 'distance_front_right']
            sensor_offset = [0, -15, 15]
        else:
            break_distance = 200
            sensor_min = 0
            sensors = ['distance_front_left', 'distance_front_right']
            sensor_offset = [0, -10, 10]
        drive_queue = queue.Queue()
        close_range_queue = queue.Queue()
        drive_queue_number = self.can_socket.create_queue(can.MsgTypes.Drive_Status.value, drive_queue)
        close_range_queue_number = self.can_socket.create_queue(can.MsgTypes.Close_Range_Dedection.value, close_range_queue)
        arrived = False
        emergency = False
        start_time = time.time()
        while (arrived is False and emergency is False and self.stop is False and self.running and
               time.time() - start_time < 12):

            my_angle = math.radians(self.my_robot.get_angle())
            my_position = self.my_robot.get_position()
            try:
                drive_msg = drive_queue.get_nowait()
                if drive_msg['status'] == 0:
                    arrived = True
                    break
            except queue.Empty:
                pass
            if self.close_range_detection:
                try:
                    range_msg = close_range_queue.get_nowait()
                    while close_range_queue.empty() is False:
                        close_range_queue.get_nowait()
                    for i, sensor in enumerate(sensors):
                        distance = max(range_msg[sensor], sensor_min)
                        if distance < break_distance:
                            if robot_big is False:
                                emergency = True
                                break
                            x = my_position[0] + math.cos(my_angle)*(distance + 90)
                            y = my_position[1] + math.sin(my_angle)*(distance + 90)
                            sensor_offset_x = math.cos(my_angle+90)*(sensor_offset[i])
                            sensor_offset_y = math.sin(my_angle+90)*(sensor_offset[i])
                            x += sensor_offset_x
                            y += sensor_offset_y
                            if (x_min < x < x_max and y_min < y < y_max) and not (stair_x[0] < x < stair_x[1] and stair_y[0] < y < stair_y[1]):
                                #print(str(sensor) + " x: " + str(x) + " y: " + str(y))
                                emergency = True
                                break
                except queue.Empty:
                    pass
            if self.enemy_detection:
                for robot in self.robots:
                    position = robot.get_position()
                    if position:
                        drive_direction = [my_position[0] + math.cos(my_angle) * (break_distance + 350),
                                           my_position[1] + math.sin(my_angle) * (break_distance + 350)]
                        line = LineString([my_position, drive_direction])
                        point = Point(position)
                        distance_from_line = point.distance(line)
                        if distance_from_line < 300:
                            emergency = True
                            break
            time.sleep(0.005)
        self.can_socket.remove_queue(close_range_queue_number)
        self.can_socket.remove_queue(drive_queue_number)
        if arrived is False:
            can_msg = {
                'type': can.MsgTypes.Emergency_Stop.value,
                'code': 0,
            }
            self.can_socket.send(can_msg)
            return False
        else:
            return True
