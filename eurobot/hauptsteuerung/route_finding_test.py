"""
This module contains the routefinding .
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import numpy as np
import math
import networkx as nx


def main():
    result = calculate_gamefield(40, 20, 20, 20, 20)
    print("finished")


def add_array(gamefield, array, pos_x, pos_y):
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


def calculate_gamefield(resolution, robot1_x, robot1_y, robot2_x, robot2_y):
    robot_size = resolution / 2
    x = resolution * 1.5
    y = resolution
    gamefield = make_table3(resolution)
    gauss = makeRobot(robot_size)
    result = add_array(gamefield, gauss, robot1_x - robot_size/2, robot1_y - robot_size/2)
    result = add_array(result, gauss, robot2_x - robot_size/2, robot2_y - robot_size/2)
    route = find_route(result)

    for point in route:
        result[point] = 120

    return result


def makeRobot(size):
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


def make_table3(size):
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
    array[int(97.8 * pixel_per_cm):int(202.2 * pixel_per_cm), 0:int(58 * pixel_per_cm)] = 100
    return array


def create_graph(gamefield):
    x_size = gamefield.shape[0]
    y_size = gamefield.shape[1]
    g = nx.Graph()
    for x in range(x_size):
        for y in range(y_size):
            g.add_node((x, y), weight=gamefield[(x, y)])
    for x in range(x_size):
        for y in range(y_size-1):
            g.add_edge((x, y), (x, y+1), weight=gamefield[(x, y)])
    for x in range(x_size-1):
        for y in range(y_size):
            g.add_edge((x, y), (x+1, y), weight=gamefield[(x, y)])
    for x in range(x_size-1):
        for y in range(y_size-1):
            g.add_edge((x, y), (x+1, y+1), weight=gamefield[(x, y)] * math.sqrt(2))
    for x in range(x_size-1):
        for y in range(1, y_size):
            g.add_edge((x, y), (x+1, y-1), weight=gamefield[(x, y)] * math.sqrt(2))
    return g


def find_route(gamefield):
    g = create_graph(gamefield)
    route = nx.astar_path(g, (1, 1), (gamefield.shape[0]-1, gamefield.shape[1]-1), heuristic=path_heuristic)
    return route


def path_heuristic(start, end):
    distance = math.sqrt((start[0] - end[0])**2 + (start[1] - end[1])**2)*1.5
    return distance

if __name__ == "__main__":
    main()