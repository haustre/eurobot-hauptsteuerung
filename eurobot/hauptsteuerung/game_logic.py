"""
This module contains classes for the game logic
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import threading
import time
import math
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


class StandsTask():
    def __init__(self, my_color):
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
            stand['collected'] = False
            stand['moved'] = False

        stands_right = list(stands_left)
        for stand in stands_right:
            x, y = stand['position']
            stand['position'] = (3000-x, y)

        if my_color is 'left':
            self.my_stands = stands_left
            self.enemy_stands = stands_right
        elif my_color is 'right':
            self.my_stands = stands_right
            self.enemy_stands = stands_left
        else:
            raise Exception("Unknown team color")

    def estimate_distance(self, robot):
        robot_x, robot_y = robot.get_position()
        shortest_distance = 100000
        nearest_stand = None
        for i, stand in enumerate(self.my_stands):
            if stand['collected'] is False and stand['moved'] is False:
                stand_x, stand_y = stand['position']
                distance = math.sqrt((robot_x - stand_x)**2 + (robot_y - stand_y)**2)
                if distance < shortest_distance:
                    shortest_distance = distance
                    nearest_stand = i
        return shortest_distance, nearest_stand