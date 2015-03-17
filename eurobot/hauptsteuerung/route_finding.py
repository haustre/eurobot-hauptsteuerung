"""
This module contains the routefinding .
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import numpy as np
import networkx as nx
import math
import copy


class RouteFinding():
    def __init__(self):
        self.resolution = 200
        self.robot_weight = self._make_robot(10)
        self.table = self._make_table(self.resolution)
        self.graph = self._create_graph(self.table)

    def calculate_path(self, robot1_x, robot1_y, robot2_x, robot2_y):
        gamefield = np.copy(self.table)
        result = self._add_array(gamefield, self.robot_weight, robot1_x - 10/2, robot1_y - 10/2)
        result = self._add_array(result, self.robot_weight, robot2_x - 10/2, robot2_y - 10/2)
        route = self._find_route(result)
        return route

    def _add_array(self, gamefield, array, pos_x, pos_y):
        """ Adds an two arrays together

        :param gamefield:
        :param array:
        :param pos_x:
        :param pos_y:
        :return: sum of arrays
        """
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
        pixel_per_cm = size / 200
        x_size = int(size * 1.5)
        y_size = size
        wall_size = int(size / 20)
        wall_height = 20
        array = 1 + np.random.random((x_size, y_size)) / 2
        for y in range(wall_size):
            array[:, y] = wall_height-wall_height/wall_size*y
        for y in range(y_size-1, y_size-wall_size, -1):
            array[:, y] = wall_height-wall_height/wall_size*(y_size-y)
        for x in range(wall_size):
            array[x, :] = wall_height-wall_height/wall_size*x
        for x in range(x_size-1, x_size-wall_size, -1):
            array[x, :] = wall_height-wall_height/wall_size*(x_size-x)
        array[int(97.8 * pixel_per_cm):int(202.2 * pixel_per_cm), 0:int(58 * pixel_per_cm)] = 100  # Stairs
        return array

    def _create_graph(self, table):
        x_size = table.shape[0]
        y_size = table.shape[1]
        g = nx.Graph()
        for x in range(x_size):
            for y in range(y_size):
                g.add_node((x, y), weight=table[(x, y)])
        for x in range(x_size):
            for y in range(y_size-1):
                g.add_edge((x, y), (x, y+1), weight=table[(x, y)])
        for x in range(x_size-1):
            for y in range(y_size):
                g.add_edge((x, y), (x+1, y), weight=table[(x, y)])
        for x in range(x_size-1):
            for y in range(y_size-1):
                g.add_edge((x, y), (x+1, y+1), weight=table[(x, y)] * math.sqrt(2))
        for x in range(x_size-1):
            for y in range(1, y_size):
                g.add_edge((x, y), (x+1, y-1), weight=table[(x, y)] * math.sqrt(2))
        return g

    def _find_route(self, weights):
        g = self._create_graph(weights)
        route = nx.astar_path(g, (1, 2), (99, 89), heuristic=self._path_heuristic)
        return route

    def _path_heuristic(self, start, end):
        distance = math.sqrt((start[0] - end[0])**2 + (start[1] - end[1])**2)*1.5
        return distance

if __name__ == "__main__":
    rout_finder = RouteFinding()
    route = rout_finder.calculate_path(30, 30, 50, 50)
    print(route)