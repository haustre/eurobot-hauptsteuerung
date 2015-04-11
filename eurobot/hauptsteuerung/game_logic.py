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
import copy


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

    def send_task_command(self, msg_id, command, blocking=False):  # TODO: Not tested
        can_msg = {
            'type': msg_id,
            'command': command,
        }
        self.can_socket.send(can_msg)
        if blocking:
            self.wait_for_task(msg_id, 0)

    def wait_for_task(self, msg_id, value):
        can_queue = queue.Queue()
        queue_number = self.can_socket.create_queue(msg_id, can_queue)
        finished = False
        while finished is False:
            can_msg = can_queue.get()
            if can_msg['state'] == value:
                finished = True
        self.can_socket.remove_queue(queue_number)


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

        if my_color == 'left':
            self.my_path = path_left
        elif my_color == 'right':
            self.my_path = path_right
        else:
            raise Exception("Unknown team color")

    def goto_task(self):
        return self.my_path['bottom']

    def do_task(self):
        self._send_command(self.climbing_command['bottom'])
        self.can_socket.send_path([], self.my_path['bottom'][0:1], self.my_path['bottom'][2], blocking=True)
        self._send_command(self.climbing_command['middle'])
        self.can_socket.send_path([], self.my_path['beginning'][0:1], self.my_path['beginning'][2], blocking=True)
        self._send_command(self.climbing_command['top'])
        self.can_socket.send_path([], self.my_path['top'][0:1], self.my_path['top'][2], blocking=True)
        self.can_socket.send_path([], self.my_path['carpet 1'][0:1], self.my_path['carpet 1'][2], blocking=True)
        self._send_command(self.my_path['fire 1'])
        self.can_socket.send_path([], self.my_path['carpet 2'][0:1], self.my_path['carpet 2'][2], blocking=True)
        self._send_command(self.my_path['fire 2'])

    def _goto_position(self, waypoint):
        can_msg = {
            'type': can.MsgTypes.Goto_Position.value,
            'x_position': self.my_path[waypoint][0],
            'y_position': self.my_path[waypoint][1],
            'angle': self.my_path[waypoint][3],
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
        self.distance_to_stand = 200
        self.points_game_element = 3
        self.command = {'blocked': 0, 'ready collect': 1, 'ready platform': 2, 'open case': 3}
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

        stands_right = copy.deepcopy(stands_left)
        for stand in stands_right:
            x, y = stand['position']
            stand['position'] = (3000-x, y)
        if my_color == 'left':
            self.my_game_elements = stands_left
            self.enemy_game_elements = stands_right
        elif my_color == 'right':
            self.my_game_elements = stands_right
            self.enemy_game_elements = stands_left
        else:
            raise Exception("Unknown team color")

    def goto_task(self, object_number):
        return self.my_game_elements[object_number]['position'], self.my_game_elements[object_number]['angle']

    def do_task(self, object_number):
        starting_point = self.robots['me'].get_position()
        stand_point = self.my_game_elements[object_number]['position']
        can_msg = {
            'type': can.MsgTypes.Stands_Command.value,
            'command': self.command['ready collect'],
        }
        self.can_socket.send(can_msg)
        point1, _ = self.calculate_stopping_point(starting_point, stand_point, self.distance_to_stand + 60)
        point2, angle = self.calculate_stopping_point(starting_point, stand_point, self.distance_to_stand - 30)
        self.can_socket.send_path([point1], point2, angle, path_speed=70, end_speed=10, blocking=True)
        #self.wait_for_task(can.MsgTypes.Stands_Status.value, 0)
        can_msg = {
            'type': can.MsgTypes.Stands_Command.value,
            'command': self.command['blocked'],
        }
        self.can_socket.send(can_msg)

    def calculate_stopping_point(self, from_pos, to_pos, distance):
        stopping_point = [0, 0]
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        angle = math.atan2(dy, dx)
        x = math.cos(angle) * distance
        y = math.sin(angle) * distance
        stopping_point[0] = int(to_pos[0] - x)
        stopping_point[1] = int(to_pos[1] - y)
        return stopping_point, angle / (2 * math.pi) * 360


class CupTask(Task):
    def __init__(self, robots, my_color, can_socket):
        super().__init__(robots, can_socket, can.MsgTypes.Stands_Command.value)
        self.my_color = my_color
        self.distance = 200
        self.shift = 100
        self.points_game_element = 3
        self.free_arms = {'right': True, 'left': True}
        self.command = {'blocked': 0, 'ready collect': 1, 'open case': 2}
        cups_left = [{'position': (250, 1750)},
                     {'position': (910, 830)},
                     {'position': (1500, 1650)},
                     {'position': (2090, 830)},
                     {'position': (2750, 1750)}
                     ]

        for stand in cups_left:
            stand['moved'] = False
        self.my_game_elements = cups_left
        self.enemy_game_elements = None

    def goto_task(self, object_number):
        return self.my_game_elements[object_number]['position']

    def do_task(self, object_number):
        starting_point = self.robots['me'].get_position()
        stand_point = self.my_game_elements[object_number]['position']
        can_msg = {
            'type': can.MsgTypes.Cup_Command.value,
            'command': self.command['ready collect'],
        }
        self.can_socket.send(can_msg)
        point1, point2, angle = self.calculate_stopping_points(starting_point, stand_point, self.distance, self.shift)
        self.can_socket.send_path([point1], point2, angle, path_speed=20, end_speed=10, blocking=True)
        #self.wait_for_task(can.MsgTypes.Stands_Status.value, 0)
        can_msg = {
            'type': can.MsgTypes.Cup_Command.value,
            'command': self.command['blocked'],
        }
        self.can_socket.send(can_msg)

    def calculate_stopping_points(self, from_pos, to_pos, distance, shift):
        point1 = [0, 0]
        point2 = [0, 0]

        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        angle = math.atan2(dy, dx)
        x = math.cos(angle) * distance
        y = math.sin(angle) * distance
        point1[0] = int(to_pos[0] - x)
        point1[1] = int(to_pos[1] - y)

        x = math.cos(angle-math.pi/2) * shift
        y = math.sin(angle-math.pi/2) * shift
        point1[0] = int(point1[0] - x)
        point1[1] = int(point1[1] - y)

        x = math.cos(angle) * 50
        y = math.sin(angle) * 50
        point2[0] = int(point1[0] + x)
        point2[1] = int(point1[1] + y)

        return point1, point2, angle / (2 * math.pi) * 360


class ClapperTask(Task):
    def __init__(self, robots, my_color, can_socket):
        super().__init__(robots, can_socket, can.MsgTypes.Clapper_Command.value)
        self.points_game_element = 5
        self.movable = False
        y_pos = 1740
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

        if my_color == 'left':
            self.my_game_elements = clapper_left
            self.enemy_game_elements = clapper_right
        elif my_color == 'right':
            self.my_game_elements = clapper_right
            self.enemy_game_elements = clapper_left
        else:
            raise Exception("Unknown team color")

    def goto_task(self, clapper_number):
        return self.my_game_elements[clapper_number]['position'], self.my_game_elements[clapper_number]['angle']

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
            'angle': self.my_game_elements[clapper_number]['angle'] * 100,
            'speed': -25,    # TODO: check
            'path_length': 0,
        }
        self.can_socket.send(can_msg)
        can_msg = {
            'type': can.MsgTypes.Clapper_Command.value,
            'command': 0,   # both arms up
        }
        self.can_socket.send(can_msg)
        time.sleep(0.2)