"""
This module contains classes for the game logic
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import threading
import time
import math
import queue
from libraries import can


class Countdown():
    def __init__(self, can_socket):
        """
        This class counts down the remaining time till the end of the game
        """
        self.can_socket = can_socket
        self.running = False
        self.start_time = 0
        self.game_time = 90  # Time the end of the game in seconds
        self.timers_to_start = []
        self.timer_loop = threading.Thread(target=self._loop)
        self.timer_loop.setDaemon(1)

    def start(self):
        self.start_time = time.time()
        self.running = True
        for timer in self.timers_to_start:
            threading.Timer(timer).start()
        self.timer_loop.start()

    def time_left(self):
        if self.running:
            time_left = int(self.game_time - (time.time() - self.start_time))
        else:
            time_left = False
        return time_left

    def set_interrupt(self, object_to_call, interrupt_name, time_left):
        if self.running:
            interrupt_time = self.game_time - time_left
            threading.Timer(interrupt_time, object_to_call, [interrupt_name]).start()
        else:
            call = object_to_call, interrupt_name, time_left
            self.timers_to_start.append(call)

    def _loop(self):
        time_left = 90
        while time_left >= 0:
            print(int(time_left))
            can_msg = {
                'type': can.MsgTypes.Game_End.value,
                'time_to_game_end': int(time_left)
            }
            if self.can_socket:
                self.can_socket.send(can_msg)
            time.sleep(0.99)
            time_left = self.start_time + self.game_time - time.time()


class Task():
    def __init__(self, robots, can_socket, can_id):
        self.robots = robots
        can_socket.create_interrupt(can_id, self.can_command)
        can_socket.create_interrupt(can_id+1, self.can_status)
        self.my_game_elements = [None]
        self.collected = 0

    def estimate_distance(self, robot):
        robot_x, robot_y = robot.get_position()
        shortest_distance = None
        nearest_element = None
        for i, stand in enumerate(self.my_game_elements):
            if stand['moved'] is False:
                stand_x, stand_y = stand['position']
                distance = math.sqrt((robot_x - stand_x)**2 + (robot_y - stand_y)**2)
                if distance < shortest_distance:
                    shortest_distance = distance
                    nearest_element = i
        return shortest_distance, nearest_element

    def check_if_moved(self):
        for robot in self.robots:
            drive_map = robot.get_map()
            for game_element in self.my_game_elements:
                x, y = game_element['position']
                if drive_map[x, y]:
                    game_element['moved'] = True

    def can_command(self, can_msg):
        pass

    def can_status(self, can_msg):
        self.collected = can_msg['collected_pieces']


class StandsTask(Task):
    def __init__(self, robots, my_color, can_socket):
        super().__init__(robots, can_socket, can.MsgTypes.Stands_Command.value)
        self.points_per_stand = 3
        stands_left = [{'position': (90, 200)},
                       {'position': (90, 1750)},
                       {'position': (90, 1850)},
                       {'position': (850, 100)},
                       {'position': (850, 200)},
                       {'position': (870, 1355)},
                       {'position': (1100, 1770)},
                       {'position': (1300, 1400)},
                       ]

        for stand in stands_left:
            stand['moved'] = False

        stands_right = list(stands_left)
        for stand in stands_right:
            x, y = stand['position']
            stand['position'] = (3000-x, y)

        if my_color is 'left':
            self.my_game_elements = stands_left
            self.enemy_stands = stands_right
        elif my_color is 'right':
            self.my_game_elements = stands_right
            self.enemy_stands = stands_left
        else:
            raise Exception("Unknown team color")

