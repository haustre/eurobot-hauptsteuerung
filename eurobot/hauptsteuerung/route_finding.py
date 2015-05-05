"""
This module contains the routefinding .
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import numpy as np
import networkx as nx
import math
import threading
from scipy.ndimage import morphology
from libraries import can


class RouteFinding():
    """ This class calculates the path from the robot to an other point on the game table """
    def __init__(self, can_socket):
        self.resolution = 40
        self.table_size = 2000
        self.robot_size = 16
        self.scale = self.table_size / self.resolution
        self.robot_weight = self._make_robot(self.robot_size)
        self.table = self._make_table(self.resolution)
        self.graph = self._create_graph(self.table)
        self.my_robot = None
        self.robots = []
        self.close_range_robots = []
        self.lock_close_range = threading.Lock()
        can_socket.create_interrupt(can.MsgTypes.Close_Range_Dedection.value, self.can_close_range_detection)

    def add_my_robot(self, robot):
        """ adds a reference to the robot

        :param robot: robot where tho program is running on
        :return: None
        """
        self.my_robot = robot

    def add_robot(self, robot):
        """ adds a reference to the robot

        :param robot: robot
        :return: None
        """
        self.robots.append(robot)

    def calculate_path(self, target):
        """ calculates the path from the robot to the destination
        All other robots are drawn in the weight map. If no data of the robot positions is available
        the close range detection data is used.

        :param target: destination
        :return: path to the destination
        """
        target = target[0:2]    # remove angle
        robot_position_unknown = False
        gamefield = np.copy(self.table)
        for robot in self.robots:
            position = robot.get_position()
            if position:
                x, y = position
                position = (int(x/self.scale), int(y/self.scale))
                gamefield = self._add_array(gamefield, self.robot_weight, position)
            else:
                robot_position_unknown = True
        if robot_position_unknown:
            with self.lock_close_range:
                robots = self.close_range_robots
            for robot in robots:
                x, y = robot
                position = (int(x/self.scale), int(y/self.scale))
                gamefield = self._add_array(gamefield, self.robot_weight, position)
        x, y = target
        target = (int(y/self.scale), int(x/self.scale))
        x, y = self.my_robot.get_position()
        my_position = (int(y/self.scale), int(x/self.scale))
        path, path_len = self._find_route(gamefield, my_position, target)
        path[:] = [(int(x*self.scale), int(y*self.scale)) for y, x in path]
        self.filter_path(path)
        return path, path_len

    def filter_path(self, path):
        """ filters out waypoints near the robot.
        This reduces the risk ouf timing problems if a route is calculated while the robot is moving

        :param path: path to filter
        :return: filtered path
        """
        del path[len(path)-1]
        # look if point is near the robot
        x, y = self.my_robot.get_position()
        for i, point in enumerate(path):
            if abs(point[0] - x) < 100 or abs(point[1] - y) < 100:
                del path[i]

    def can_close_range_detection(self, can_msg):
        """ calculates the position of an other robot in the way with the data of the closerange detection """
        if self.my_robot:
            my_x, my_y = self.my_robot.get_position()
            my_angle = self.my_robot.get_angle() / 100
            with self.lock_close_range:
                self.close_range_robots = []
                if can_msg['front_left_correct']:
                    sensor_angle = - 20
                    x = my_x + math.cos(math.radians(my_angle+sensor_angle))*can_msg['distance_front_left']
                    y = my_y + math.sin(math.radians(my_angle+sensor_angle))*can_msg['distance_front_left']
                    if 0 < x < 3000 and 0 < y < 2000:
                        self.close_range_robots.append((x, y))
                if can_msg['front_middle_correct']:
                    x = my_x + math.cos(math.radians(my_angle))*can_msg['distance_front_middle']
                    y = my_y + math.sin(math.radians(my_angle))*can_msg['distance_front_middle']
                    if 0 < x < 3000 and 0 < y < 2000:
                        self.close_range_robots.append((x, y))
                if can_msg['front_right_correct']:
                    sensor_angle = 20
                    x = my_x + math.cos(math.radians(my_angle+sensor_angle))*can_msg['distance_front_right']
                    y = my_y + math.sin(math.radians(my_angle+sensor_angle))*can_msg['distance_front_right']
                    if 0 < x < 3000 and 0 < y < 2000:
                        self.close_range_robots.append((x, y))

    def _add_array(self, gamefield, array, position):
        """ Adds an two arrays together

        :param gamefield: table array
        :param array: array to add
        :param pos_x: x position where to add the array
        :param pos_y: y position where to add the array
        :return: sum of arrays
        """
        pos_y, pos_x = position
        pos_x -= self.robot_size / 2
        pos_y -= self.robot_size / 2
        v_range1 = slice(max(0, pos_x), max(min(pos_x + array.shape[0], gamefield.shape[0]), 0))
        h_range1 = slice(max(0, pos_y), max(min(pos_y + array.shape[1], gamefield.shape[1]), 0))

        v_range2 = slice(max(0, -pos_x), min(-pos_x + gamefield.shape[0], array.shape[0]))
        h_range2 = slice(max(0, -pos_y), min(-pos_y + gamefield.shape[1], array.shape[1]))
        gamefield[v_range1, h_range1] += array[v_range2, h_range2]
        return gamefield

    def _make_robot(self, size):
        """ creates a weight array of a robot with a given size

        :param size: size of the robot
        :return: weight array of the robot
        """
        scale = 1/(size/self.resolution)
        x = np.arange(0, size, 1, float)
        y = x[:, np.newaxis]
        x0 = y0 = size // 2
        array = 25 - np.sqrt(((x-x0)*scale)**2 + ((y-y0)*scale)**2)
        array = array.clip(min=0)
        return array

    def _make_table(self, size):
        """ creates a weight map of the table

        :param size: y resolution of the generated table
        :return: map of the table
        """
        weight = 100000
        pixel_per_mm = size / 2000
        x_size = int(size * 1.5)
        y_size = size
        wall_size = int(size / 20)
        #array = 1 + np.random.random((y_size, x_size)) / 2
        array = np.ones((y_size, x_size))
        for y in range(wall_size):
            array[y, :] = weight-weight/wall_size*y
        for y in range(y_size-1, y_size-wall_size-1, -1):
            array[y, :] = weight-weight/wall_size*(y_size-y-1)
        for x in range(wall_size):
            array[:, x] = weight-weight/wall_size*x
        for x in range(x_size-1, x_size-wall_size-1, -1):
            array[:, x] = weight-weight/wall_size*(x_size-x-1)
        array[0:math.ceil(580 * pixel_per_mm), math.floor(978 * pixel_per_mm):math.ceil(2022 * pixel_per_mm)] = weight  # Stairs
        # yellow start
        array[math.floor(767 * pixel_per_mm):math.ceil((789+50) * pixel_per_mm), 0:math.ceil(400 * pixel_per_mm)] = weight
        array[math.floor((1211-50) * pixel_per_mm):math.ceil(1233 * pixel_per_mm), 0:math.ceil(400 * pixel_per_mm)] = weight
        # green start
        array[math.floor(767 * pixel_per_mm):math.ceil((789+50) * pixel_per_mm), math.floor(2600 * pixel_per_mm):math.ceil(3000 * pixel_per_mm)] = weight
        array[math.floor((1211-50) * pixel_per_mm):math.ceil(1233 * pixel_per_mm), math.floor(2600 * pixel_per_mm):math.ceil(3000 * pixel_per_mm)] = weight

        array[math.floor(1800 * pixel_per_mm):math.ceil(2000 * pixel_per_mm), math.floor(1100 * pixel_per_mm):math.ceil(1900 * pixel_per_mm)] = weight
        array = morphology.grey_dilation(array, size=(11, 11))
        return array

    def _create_graph(self, table):
        """ creates a graph for the A-star algorithm with the given weights

        :param table: weight array
        :return: graph
        """
        x_size = table.shape[1]
        y_size = table.shape[0]
        graph = nx.Graph()
        for x in range(x_size):
            for y in range(y_size):
                graph.add_node((y, x), weight=table[(y, x)])
        for x in range(x_size):
            for y in range(y_size-1):
                graph.add_edge((y, x), (y, x+1), weight=table[(y, x)])
        for x in range(x_size-1):
            for y in range(y_size):
                graph.add_edge((y, x), (y+1, x), weight=table[(y, x)])
        for x in range(x_size-1):
            for y in range(y_size-1):
                graph.add_edge((y, x), (y+1, x+1), weight=table[(y, x)] * math.sqrt(2))
        for x in range(x_size-1):
            for y in range(1, y_size):
                graph.add_edge((y, x), (y+1, x-1), weight=table[(y, x)] * math.sqrt(2))
        return graph

    def _find_route(self, weights, position, destination):
        """ Finds the shortest route between two points in a graph using the A-Star algorithm.

        :param weights: wight map
        :param position: position of the robot
        :param destination: node to drive to
        :return: path, total weight of the path
        """
        g = self._create_graph(weights)
        path = nx.astar_path(g, position, destination, heuristic=self._path_heuristic)
        path_len = sum(g[u][v].get('weight', 1) for u, v in zip(path[:-1], path[1:]))
        return path, path_len

    def _path_heuristic(self, start, end):
        """ heuristic for the A-star algorithm

        :param start: start position
        :param end: end position
        :return: estimated distance
        """
        distance = math.sqrt((start[0] - end[0])**2 + (start[1] - end[1])**2)*math.sqrt(2)
        return distance