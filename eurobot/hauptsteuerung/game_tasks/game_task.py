"""
This module the parent class for all game classes
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import threading
import time
import math
import queue

class Task:
    """ parent class of all game tasks """
    def __init__(self, robots, can_socket, can_id, drive):
        self.drive = drive
        self.robots = robots
        self.can_socket = can_socket
        self.can_socket.create_interrupt(can_id, self.can_command)
        self.can_socket.create_interrupt(can_id + 1, self.can_status)
        self.my_game_elements = []
        self.enemy_game_elements = []
        self.collected = 0
        self.movable = True
        self.moved_thread = threading.Thread(target=self.check_if_moved)
        self.moved_thread.setDaemon(1)
        self.moved_thread.start()

    def estimate_distances(self):
        """ gives back the nearest game element and an estimated distance to it

        :param robot: robot to estimate the distance to
        :return: distance to the game element, number of the element
        """
        robot_x, robot_y = self.robots['me'].get_position()
        distance_list = []
        for i, game_element in enumerate(self.my_game_elements):
            if game_element['moved'] is False:
                stand_x, stand_y = game_element['position']
                distance = math.sqrt((robot_x - stand_x) ** 2 + (robot_y - stand_y) ** 2)
                distance_list.append((distance, i))
        return distance_list

    def check_if_moved(self):
        """ loop checking which game elements have been moved """
        while True:
            if self.movable:
                for robot in self.robots.values():
                    if robot:
                        drive_map = robot.get_map()
                        for game_element in self.my_game_elements:
                            x, y = game_element['position']
                            x, y = int(x / 10), int(y / 10)
                            if drive_map[x, y]:
                                game_element['moved'] = True
                        for game_element in self.enemy_game_elements:
                            x, y = game_element['position']
                            x, y = int(x / 10), int(y / 10)
                            if drive_map[x, y]:
                                game_element['moved'] = True
                time.sleep(0.1)

    def can_command(self, can_msg):
        pass

    def can_status(self, can_msg):
        """ sets the count of the selected game elements according to the periphery board

        :param can_msg: CAN message from the periphery board
        :return:
        """
        self.collected = can_msg['collected_pieces']

    def send_task_command(self, msg_id, command, blocking=False):
        """ sends a command over CAN to the periphery board

        :param msg_id: CAN id
        :param command: CAN command
        :param blocking: specifies if the robot should wait for a response of the periphery board
        :return: None
        """
        can_msg = {
            'type': msg_id,
            'command': command,
        }
        self.can_socket.send(can_msg)
        if blocking:
            self.wait_for_task(msg_id + 1)

    def wait_for_task(self, msg_id):
        """ waits for a response of the periphery board

        :param msg_id: CAN id to wait for
        :return: None
        """
        can_queue = queue.Queue()
        queue_number = self.can_socket.create_queue(msg_id, can_queue)
        finished = False
        while finished is False:
            can_msg = can_queue.get()
            if can_msg['state'] < 3:
                finished = True
        self.can_socket.remove_queue(queue_number)

    def get_debug_data(self):
        """ returns the position of each game element and if it is moved
        used by the GUI to display this data

        :return: dictionary
        """
        game_elements = []
        for element in self.my_game_elements:
            game_elements.append((element['position'], element['moved']))
        for element in self.enemy_game_elements:
            game_elements.append((element['position'], element['moved']))
        return game_elements
