"""
This module contains the routefinding .
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import numpy as np
import networkx as nx
import math
import time
from scipy.ndimage import morphology


class RouteFinding():
    def __init__(self):
        self.resolution = 40
        self.table_size = 2000
        self.robot_size = 20
        self.scale = self.table_size / self.resolution
        self.robot_weight = self._make_robot(self.robot_size)
        self.table = self._make_table(self.resolution)
        self.graph = self._create_graph(self.table)
        self.my_robot = None
        self.robots = []

    def add_my_robot(self, robot):
        self.my_robot = robot

    def add_robot(self, robot):
        self.robots.append(robot)

    def calculate_path(self, target):
        gamefield = np.copy(self.table)
        for robot in self.robots:
            x, y = robot.get_position()
            position = (int(x/self.scale), int(y/self.scale))
            result = self._add_array(gamefield, self.robot_weight, position)
        #x, y = target
        #target = (int(x/self.scale), int(y/self.scale))
        x, y = self.my_robot.get_position()
        my_position = (int(y/self.scale), int(x/self.scale))
        route = self._find_route(result, my_position, target)
        route[:] = [(int(x*self.scale), int(y*self.scale)) for y, x in route]
        return route

    def _add_array(self, gamefield, array, position):
        """ Adds an two arrays together

        :param gamefield:
        :param array:
        :param pos_x:
        :param pos_y:
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
        scale = 1/(size/50)
        x = np.arange(0, size, 1, float)
        y = x[:, np.newaxis]
        x0 = y0 = size // 2
        array = 25 - np.sqrt(((x-x0)*scale)**2 + ((y-y0)*scale)**2)
        array = array.clip(min=0)
        return array

    def _make_table(self, size):
        weight = 100000
        pixel_per_mm = size / 2000
        x_size = int(size * 1.5)
        y_size = size
        wall_size = int(size / 20)
        wall_height = 20
        array = 1 + np.random.random((y_size, x_size)) / 2
        for y in range(wall_size):
            array[y, :] = wall_height-wall_height/wall_size*y
        for y in range(y_size-1, y_size-wall_size, -1):
            array[y, :] = wall_height-wall_height/wall_size*(y_size-y)
        for x in range(wall_size):
            array[:, x] = wall_height-wall_height/wall_size*x
        for x in range(x_size-1, x_size-wall_size, -1):
            array[:, x] = wall_height-wall_height/wall_size*(x_size-x)
        array[0:int(580 * pixel_per_mm), int(978 * pixel_per_mm):int(2022 * pixel_per_mm)] = weight  # Stairs
        # yellow start
        array[int(767 * pixel_per_mm):int((789+50) * pixel_per_mm), 0:int(400 * pixel_per_mm)] = weight
        array[int((1211-50) * pixel_per_mm):int(1233 * pixel_per_mm), 0:int(400 * pixel_per_mm)] = weight
        # green start
        array[int(767 * pixel_per_mm):int((789+50) * pixel_per_mm), int(2600 * pixel_per_mm):int(3000 * pixel_per_mm)] = weight
        array[int((1211-50) * pixel_per_mm):int(1233 * pixel_per_mm), int(2600 * pixel_per_mm):int(3000 * pixel_per_mm)] = weight

        array[int(1800 * pixel_per_mm):int(2000 * pixel_per_mm), int(1100 * pixel_per_mm):int(1900 * pixel_per_mm)] = weight
        array = morphology.grey_dilation(array, size=(5, 5))
        return array

    def _create_graph(self, table):
        x_size = table.shape[1]
        y_size = table.shape[0]
        g = nx.Graph()
        for x in range(x_size):
            for y in range(y_size):
                g.add_node((y, x), weight=table[(y, x)])
        for x in range(x_size):
            for y in range(y_size-1):
                g.add_edge((y, x), (y, x+1), weight=table[(y, x)])
        for x in range(x_size-1):
            for y in range(y_size):
                g.add_edge((y, x), (y+1, x), weight=table[(y, x)])
        for x in range(x_size-1):
            for y in range(y_size-1):
                g.add_edge((y, x), (y+1, x+1), weight=table[(y, x)] * math.sqrt(2))
        for x in range(x_size-1):
            for y in range(1, y_size):
                g.add_edge((y, x), (y+1, x-1), weight=table[(y, x)] * math.sqrt(2))
        return g

    def _find_route(self, weights, position, destination):
        g = self._create_graph(weights)
        route = nx.astar_path(g, position, destination, heuristic=self._path_heuristic)
        return route

    def _path_heuristic(self, start, end):
        distance = math.sqrt((start[0] - end[0])**2 + (start[1] - end[1])**2)*1.5
        return distance

if __name__ == "__main__":
    start = time.time()
    rout_finder = RouteFinding()
    print(time.time() - start)
    route = rout_finder.calculate_path(((30, 30), (50, 50)))
    print(time.time() - start)
    print(route)