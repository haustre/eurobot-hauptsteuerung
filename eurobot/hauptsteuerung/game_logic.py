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
        self.can_socket = can_socket
        self.can_socket.create_interrupt(can_id, self.can_command)
        self.can_socket.create_interrupt(can_id+1, self.can_status)
        self.my_game_elements = [None]
        self.collected = 0
        self.movable = True

    def estimate_distance(self, robot):
        robot_x, robot_y = robot.get_position()
        shortest_distance = None
        nearest_element = None
        for i, game_element in enumerate(self.my_game_elements):
            if game_element['moved'] is False:
                stand_x, stand_y = game_element['position']
                distance = math.sqrt((robot_x - stand_x)**2 + (robot_y - stand_y)**2)
                if distance < shortest_distance:
                    shortest_distance = distance
                    nearest_element = i
        return shortest_distance, nearest_element

    def check_if_moved(self):
        if self.movable:
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


class StairTask(Task):
    def __init__(self, robots, my_color, can_socket):
        super().__init__(robots, can_socket, can.MsgTypes.Climbing_Command.value)
        self.climbing_command = {'up': 0, 'bottom': 1, 'middle': 2, 'top': 3}
        self.carpet_command = {'fire right': 0, 'fire left': 1}
        path_left = {'bottom': (1200, 800, 270),
                     'beginning': (1200, 600, 270),
                     'top': (1200, 200, 270),
                     'carpet 1': (1100, 200, 290),
                     'fire 1': self.carpet_command['fire right'],
                     'carpet 2': (1370, 200, 250),
                     'fire 2': self.carpet_command['fire left']
                     }

        path_right = {'bottom': (3000 - 1200, 800, 270),
                      'beginning': (3000 - 1200, 600, 270),
                      'top': (3000 - 1200, 200, 270),
                      'carpet 1': (3000 - 1100, 200, 290),
                      'fire 1': self.carpet_command['fire left'],
                      'carpet 2': (3000 - 1370, 200, 250),
                      'fire 2': self.carpet_command['fire right']
                      }

        if my_color is 'left':
            self.my_path = path_left
        elif my_color is 'right':
            self.my_path = path_right
        else:
            raise Exception("Unknown team color")

    def goto_task(self):
        return self.my_path['bottom']

    def do_task(self):
        self._send_command(self.climbing_command['bottom'])
        time.sleep(10)
        self._goto_position('beginning')
        self._send_command(self.climbing_command['middle'])
        # TODO: drive to the top
        self._goto_position('carpet 1')
        self._send_command(self.my_path['fire 1'])
        self._goto_position('carpet 2')
        self._send_command(self.my_path['fire 2'])

    def _goto_position(self, waypoint):
        can_msg = {
            'type': can.MsgTypes.Goto_Position.value,
            'x_position': self.my_path[waypoint][0],
            'y_position': self.my_path['waypoint'][1],
            'angle': self.my_path['waypoint'][3],
            'speed': 25,    # TODO: check
            'path_length': 0,
        }
        self.can_socket.send(can_msg)

        can_queue = queue.Queue()
        queue_number = self.can_socket.create_queue(can.MsgTypes.Drive_Status.value, can_queue)
        arrived = False
        while arrived is False:
            can_msg = can_queue.get()
            if can_msg['status'] == 0 and can_msg['time_to_destination'] == 0:  # TODO: change status
                arrived = True
        self.can_socket.remove_queue(queue_number)

    def _send_command(self, command):
        can_msg = {
            'type': can.MsgTypes.Climbing_Command.value,
            'command': command,
        }
        self.can_socket.send(can_msg)
        # TODO: wait to finish


class StandsTask(Task):
    def __init__(self, robots, my_color, can_socket):
        super().__init__(robots, can_socket, can.MsgTypes.Stands_Command.value)
        self.points_game_element = 3
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


class ClapperTask(Task):
    def __init__(self, robots, my_color, can_socket):
        super().__init__(robots, can_socket, can.MsgTypes.Clapper_Command.value)
        self.points_game_element = 5
        self.movable = False
        y_pos = 1700
        clapper_left = [{'position': (300, y_pos), 'side': 'right', 'angle': 0, 'end_position': (500, y_pos)},
                        {'position': (900, y_pos), 'side': 'right', 'angle': 0, 'end_position': (1100, y_pos)},
                        {'position': (2400, y_pos), 'side': 'left', 'angle': 180, 'end_position': (2200, y_pos)}
                        ]

        clapper_right = [{'position': (2700, y_pos), 'side': 'left', 'angle': 180, 'end_position': (2500, y_pos)},
                         {'position': (2100, y_pos), 'side': 'left', 'angle': 180, 'end_position': (1900, y_pos)},
                         {'position': (600, y_pos), 'side': 'right', 'angle': 0, 'end_position': (800, y_pos)}
                         ]

        for clapper in clapper_left:
            clapper['moved'] = False

        for clapper in clapper_right:
            clapper['moved'] = False

        if my_color is 'left':
            self.my_game_elements = clapper_left
            self.enemy_game_elements = clapper_right
        elif my_color is 'right':
            self.my_game_elements = clapper_right
            self.enemy_game_elements = clapper_left
        else:
            raise Exception("Unknown team color")

    def goto_task(self, clapper_number):
        return self.my_game_elements[clapper_number]['position'], self.my_game_elements[clapper_number]['angle'] * 100

    def do_task(self, clapper_number):
        if self.my_game_elements[clapper_number]['side'] == 'left':
            clapper_side = 2
        else:
            clapper_side = 1
        can_msg = {
            'type': can.MsgTypes.Clapper_Command.value,
            'command': clapper_side,
        }
        self.can_socket.send(can_msg)
        time.sleep(1)
        # TODO: check if the way is free
        can_msg = {
            'type': can.MsgTypes.Goto_Position.value,
            'x_position': self.my_game_elements[clapper_number]['end_position'][0],
            'y_position': self.my_game_elements[clapper_number]['end_position'][1],
            'angle': self.my_game_elements[clapper_number]['angle'][0] * 100,
            'speed': 25,    # TODO: check
            'path_length': 0,
        }
        self.can_socket.send(can_msg)
        can_msg = {
            'type': can.MsgTypes.Clapper_Command.value,
            'command': 0,   # both arms up
        }
        self.can_socket.send(can_msg)
        time.sleep(0.2)