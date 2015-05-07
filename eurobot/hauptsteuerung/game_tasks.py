"""
This module contains the countdown and all classes for the game logic
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
        """ This class counts down the remaining time till the end of the game """
        self.can_socket = can_socket
        self.running = False
        self.start_time = 0
        self.game_time = 90  # Time the end of the game in seconds
        self.timers_to_start = []
        self.timer_loop = threading.Thread(target=self._loop)
        self.timer_loop.setDaemon(1)

    def start(self):
        """ starts the countdown

        :return: None
        """
        self.start_time = time.time()
        self.running = True
        for timer in self.timers_to_start:
            threading.Timer(timer).start()
        self.timer_loop.start()

    def time_left(self):
        """ returns the time left to the end of the game or false if the game is not started

        :return: time left until game end
        """
        if self.running:
            time_left = int(self.game_time - (time.time() - self.start_time))
        else:
            time_left = False
        return time_left

    def set_interrupt(self, object_to_call, interrupt_name, time_left):
        """ creates a new interrupt

        :param object_to_call: this object gets called at the specified time
        :param interrupt_name: name of the interrupt
        :param time_left: time to call the object
        :return: None
        """
        if self.running:
            interrupt_time = self.game_time - time_left
            threading.Timer(interrupt_time, object_to_call, [interrupt_name]).start()
        else:
            call = object_to_call, interrupt_name, time_left
            self.timers_to_start.append(call)

    def _loop(self):
        """ loop counting down the remaining time """
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
    """ parent class of all game tasks """
    def __init__(self, robots, can_socket, can_id, drive):
        self.drive = drive
        self.robots = robots
        self.can_socket = can_socket
        self.can_socket.create_interrupt(can_id, self.can_command)
        self.can_socket.create_interrupt(can_id+1, self.can_status)
        self.my_game_elements = []
        self.enemy_game_elements = []
        self.collected = 0
        self.movable = True
        self.moved_thread = threading.Thread(target=self.check_if_moved)
        self.moved_thread.setDaemon(1)
        self.moved_thread.start()

    def estimate_distance(self):
        """ gives back the nearest game element and an estimated distance to it

        :param robot: robot to estimate the distance to
        :return: distance to the game element, number of the element
        """
        robot_x, robot_y = self.robots['me'].get_position()
        shortest_distance = 9000  # Not on the Table
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
        """ loop checking which game elements have been moved """
        while True:
            if self.movable:
                for robot in self.robots.values():
                    if robot:
                        drive_map = robot.get_map()
                        for game_element in self.my_game_elements:
                            x, y = game_element['position']
                            x, y = int(x/10), int(y/10)
                            if drive_map[x, y]:
                                game_element['moved'] = True
                        for game_element in self.enemy_game_elements:
                            x, y = game_element['position']
                            x, y = int(x/10), int(y/10)
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
            self.wait_for_task(msg_id+1)

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


class StairTask(Task):
    """ Class for driving to the top of the stair """
    def __init__(self, robots, my_color, can_socket, drive):
        super().__init__(robots, can_socket, can.MsgTypes.Climbing_Command.value, drive)
        self.climbing_command = {'up': 0, 'bottom': 1, 'middle': 2, 'top': 3}
        self.carpet_command = {'fire right': 0, 'fire left': 1}
        path_left = {'in_front': (1250, 1080, 270),
                     'bottom': (1250, 675, 270),
                     'beginning': (1250, 650, 270),
                     'top': (1250, 190, 270),
                     'carpet 1': (1080, 200, 180),
                     'fire 1': self.carpet_command['fire left'],
                     'turning point': (1250, 200, 270),
                     'carpet 2': (1400, 200, 0),
                     'fire 2': self.carpet_command['fire right']
                     }
        path_right = {}
        for key, value in path_left.items():
            if type(value) is not int:
                path_right[key] = 3000 - value[0], value[1], value[2]
            elif value == 1:
                path_right[key] = 0
            elif value == 0:
                path_right[key] = 1
        x, y, angle = path_right['carpet 1']
        path_right['carpet 1'] = x, y, angle + 180
        x, y, angle = path_right['carpet 2']
        path_right['carpet 2'] = x, y, angle + 180
            #fire1 = path_right['fire 1']
            #fire2 = path_right['fire 2']
            #path_right['fire 1'] = fire2
            #path_right['fire 2'] = fire1

        if my_color == 'left':
            self.my_path = path_left
        elif my_color == 'right':
            self.my_path = path_right
        else:
            raise Exception("Unknown team color")

    def goto_task(self):
        """ returns the position information of the stair

        :return: position, angle
        """
        return self.my_path['in_front'][0:2], self.my_path['in_front'][2]

    def do_task(self):
        """ drives to the top of the stair """
        self.drive.drive_path([], self.my_path['bottom'], None, blocking=False)  # TODO: Danger no close range detection
        self.send_task_command(can.MsgTypes.Climbing_Command.value, self.climbing_command['bottom'], blocking=True)
        timer = threading.Timer(2, self.send_climbing_top)
        timer.setDaemon(True)
        timer.start()
        self.drive.drive_path([], self.my_path['top'], None)

        myY, myY = self.robots['me'].get_position()

        while myY > 290:
            self.drive.drive_path([], self.my_path['top'], None)
            myY, myY = self.robots['me'].get_position()

        self.send_task_command(can.MsgTypes.Climbing_Command.value, self.climbing_command['up'], blocking=True)
        self.drive.drive_path([], self.my_path['carpet 1'], None)
        self.send_task_command(can.MsgTypes.Carpet_Command.value, self.my_path['fire 1'], blocking=True)
        self.drive.drive_path([], self.my_path['top'], None, end_speed=(-self.drive.speed))
        self.drive.drive_path([], self.my_path['carpet 2'], None)
        self.send_task_command(can.MsgTypes.Carpet_Command.value, self.my_path['fire 2'], blocking=True)

    def send_climbing_top(self):
        self.send_task_command(can.MsgTypes.Climbing_Command.value, self.climbing_command['top'])


class StandsTask(Task):
    """ Class collecting the stands """
    def __init__(self, robots, my_color, can_socket, drive):
        super().__init__(robots, can_socket, can.MsgTypes.Stands_Command.value, drive)
        self.distance_to_stand = 200
        self.points_game_element = 6
        empty_position = {'start_position': (1300, 1650, 90), 'position': (1300, 1760, 90)}
        self.command = {'blocked': 0, 'ready collect': 1, 'ready platform': 2, 'open case': 3}
        stands_left = [{'position': (90, 200), 'start position': (290, 490)},
                       {'position': (90, 1750), 'start position': (290, 1460)},
                       #{'position': (90, 1850), 'start position': None},
                       #{'position': (850, 100), 'start position': None},
                       {'position': (850, 200), 'start position': (650, 490)},
                       {'position': (870, 1355), 'start position': None},
                       {'position': (1100, 1770), 'start position': None},
                       {'position': (1300, 1400), 'start position': None},
                       ]

        for stand in stands_left:
            stand['moved'] = False

        stands_right = copy.deepcopy(stands_left)
        for stand in stands_right:
            x, y = stand['position']
            stand['position'] = (3000-x, y)
            if stand['start position'] is not None:
                x, y = stand['start position']
                stand['start position'] = (3000-x, y)
        if my_color == 'left':
            self.my_game_elements = stands_left
            self.enemy_game_elements = stands_right
            self.empty_position = empty_position
        elif my_color == 'right':
            self.empty_position = {}
            self.my_game_elements = stands_right
            self.enemy_game_elements = stands_left
            x, y, angle = empty_position['start_position']
            self.empty_position['start_position'] = 3000 - x, y, angle
            x, y, angle = empty_position['position']
            self.empty_position['position'] = 3000 - x, y, angle
        else:
            raise Exception("Unknown team color")

    def goto_task(self, object_number):  # TODO: Calculate Point in front of the stand
        """ returns the position information of the specified stand

        :param object_number: specifies which game element is chosen
        :return: position, angle
        """
        return self.my_game_elements[object_number]['start position'], None

    def do_task(self, object_number):
        """ collects the chosen stand

        :param object_number:  specifies which game element is chosen
        """
        starting_point = self.robots['me'].get_position()
        stand_point = self.my_game_elements[object_number]['position']
        self.send_task_command(can.MsgTypes.Stands_Command.value, self.command['ready collect'])
        point1 = self.calculate_stopping_point(starting_point, stand_point, 30)
        point2 = self.calculate_stopping_point(starting_point, stand_point, -50)
        self.drive.drive_path([point1[0:2]], point2[0:2], None,  end_speed=10)
        time.sleep(0.7)
        #threading.Timer(0.5, self.send_task_command(can.MsgTypes.Stands_Command.value, self.command['blocked'])).start()

    def calculate_stopping_point(self, from_pos, to_pos, distance):
        """ calculates the correct position to collect the stand

        :param from_pos: position of the robot
        :param to_pos: position of the stand
        :param distance: distance to the stand
        :return: point to drive to, angle
        """
        distance += self.distance_to_stand
        stopping_point = [0, 0]
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        angle = math.atan2(dy, dx)
        x = math.cos(angle) * distance
        y = math.sin(angle) * distance
        stopping_point[0] = int(to_pos[0] - x)
        stopping_point[1] = int(to_pos[1] - y)
        return stopping_point[0], stopping_point[1], angle / (2 * math.pi) * 360

    def goto_empty(self):
        """ returns the position information of the place to put the stands to

        :return: position with angle
        """
        return self.empty_position['start_position']

    def do_empty(self):
        """ puts down the stands """
        self.send_task_command(can.MsgTypes.Stands_Command.value, self.command['ready platform'], blocking=True)
        self.drive.drive_path([], self.empty_position['position'], None, end_speed=15)
        self.send_task_command(can.MsgTypes.Stands_Command.value, self.command['open case'], blocking=True)
        self.drive.drive_path([], self.empty_position['start_position'], None, end_speed=-15)
        self.send_task_command(can.MsgTypes.Stands_Command.value, self.command['ready collect'])
        self.send_task_command(can.MsgTypes.Stands_Command.value, self.command['blocked'])


class CupTask(Task):
    """ Class collecting the cups """
    def __init__(self, robots, my_color, can_socket, drive):
        super().__init__(robots, can_socket, can.MsgTypes.Cup_Command.value, drive)
        self.my_color = my_color
        self.distance = 150
        self.shift = 100
        self.points_game_element = -1000  # TODO: points = 3
        self.free_arms = {'right': True, 'left': True}
        self.command = {'blocked': 0, 'ready collect': 1, 'open case': 2}
        self.sides = {'left': 0, 'right': 1}
        cups_left = [{'position': (250, 1750)},
                     {'position': (910, 830)},
                     {'position': (1500, 1650)},
                     {'position': (2090, 830)},
                     {'position': (2750, 1750)}
                     ]

        for stand in cups_left:
            stand['moved'] = False
        self.my_game_elements = cups_left

    def goto_task(self, object_number):
        """ returns the position information of the specified cup

        :param object_number: specifies which game element is chosen
        :return: position, angle
        """
        return self.my_game_elements[object_number]['position'], None  # TODO: set correct position

    def do_task(self, object_number):
        """ collects the chosen cup

        :param object_number:  specifies which game element is chosen
        """
        starting_point = self.robots['me'].get_position()
        stand_point = self.my_game_elements[object_number]['position']
        self.send_task_command(can.MsgTypes.Cup_Command.value, self.command['ready collect'])
        point1, point2, angle = self.calculate_stopping_points(starting_point, stand_point, self.sides['right'])
        self.drive.drive_path([point1], point2, angle, end_speed=10)
        time.sleep(0.2)

    def calculate_stopping_points(self, from_pos, to_pos, side):
        """ calculates the correct position to collect the cup

        :param from_pos: position of the robot
        :param to_pos: position of the stand
        :param side: which side is used to collect the cup
        :return: point to drive to, angle
        """
        point1 = [0, 0]
        point2 = [0, 0]

        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        angle = math.atan2(dy, dx)
        x = math.cos(angle) * self.distance
        y = math.sin(angle) * self.distance
        point1[0] = int(to_pos[0] - x)
        point1[1] = int(to_pos[1] - y)

        if side == self.sides['left']:
            x = math.cos(angle-math.pi/2) * self.shift
            y = math.sin(angle-math.pi/2) * self.shift
        else:
            x = math.cos(angle+math.pi/2) * self.shift
            y = math.sin(angle+math.pi/2) * self.shift
        point1[0] = int(point1[0] - x)
        point1[1] = int(point1[1] - y)

        x = math.cos(angle) * 50
        y = math.sin(angle) * 50
        point2[0] = int(point1[0] + x)
        point2[1] = int(point1[1] + y)
        return point1, (point2[0], point2[1]), angle / (2 * math.pi) * 360


class ClapperTask(Task):
    """ Class for closing the clappers """
    def __init__(self, robots, my_color, can_socket, drive):
        super().__init__(robots, can_socket, can.MsgTypes.Clapper_Command.value, drive)
        self.points_game_element = 5
        self.movable = False
        self.command = {'up': 0, 'right': 1, 'left': 2}
        self.angle = 90
        self.distance = 260
        clapper_left = [{'position': (300, 2000), 'side': 'right'},
                        {'position': (900, 2000), 'side': 'right'},
                        {'position': (2400, 2000), 'side': 'left'}
                        ]

        clapper_right = [{'position': (2700, 2000), 'side': 'left'},
                         {'position': (2100, 2000), 'side': 'left'},
                         {'position': (600, 2000), 'side': 'right'}
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
        """ returns the position information of the specified clapper

        :param clapper_number: specifies which game element is chosen
        :return: position, angle
        """
        (x, y), angle = self.my_game_elements[clapper_number]['position'], self.angle
        y -= self.distance
        return (x, y), angle

    def do_task(self, clapper_number):
        """ closes the chosen clapper

        :param clapper_number:  specifies which game element is chosen
        """
        side = self.my_game_elements[clapper_number]['side']
        self.send_task_command(can.MsgTypes.Clapper_Command.value, self.command[side], blocking=True)
        if side == 'right':
            angle = 0
        else:
            angle = 180
        self.drive.drive_path([], None, angle, end_speed=10)
        self.send_task_command(can.MsgTypes.Clapper_Command.value, self.command['up'])
        self.my_game_elements[clapper_number]['moved'] = True


class PopcornTask(Task):
    """ Class for collecting the popcorn from the popcorn machine """
    def __init__(self, robots, my_color, can_socket, drive):
        super().__init__(robots, can_socket, can.MsgTypes.Stands_Command.value, drive)
        self.points_game_element = 3
        self.angle = 90
        self.distance = 130
        empty_position = {'start_position': (500, 1000, 0), 'position': (220, 1000, 0)}
        self.command = {'ready collect': 0, 'open case': 1, }
        popcorn_left = [{'start_position': (300, 400), 'position': (300, 0)},
                        {'start_position': (600, 400), 'position': (600, 0)}
                        ]

        for popcorn in popcorn_left:
            popcorn['moved'] = False

        popcorn_right = copy.deepcopy(popcorn_left)
        for popcorn in popcorn_right:
            x, y = popcorn['start_position']
            popcorn['start_position'] = (3000-x, y)
            x, y = popcorn['position']
            popcorn['position'] = (3000-x, y)
        if my_color == 'left':
            self.my_game_elements = popcorn_left
            self.enemy_game_elements = popcorn_right
            self.empty_position = empty_position
        elif my_color == 'right':
            self.empty_position = {}
            self.my_game_elements = popcorn_right
            self.enemy_game_elements = popcorn_left
            x, y, angle = empty_position['start_position']
            self.empty_position['start_position'] = 3000 - x, y, 180
            x, y, angle = empty_position['position']
            self.empty_position['position'] = 3000 - x, y, 180

        else:
            raise Exception("Unknown team color")

    def goto_task(self, object_number):
        """ returns the position information of the specified popcorn machine

        :param object_number: specifies which game element is chosen
        :return: position, angle
        """
        if object_number < 2:
            return self.my_game_elements[object_number]['start_position'], self.angle
        else:
            object_number -= 2
            return self.enemy_game_elements[object_number]['start_position'], self.angle

    def do_task(self, object_number):
        """ collecting the popcorn from the chosen popcorn machine

        :param object_number:  specifies which game element is chosen
        """
        if object_number < 2:
            self.send_task_command(can.MsgTypes.Popcorn_Command.value, self.command['ready collect'], blocking=False)
            x, y = self.my_game_elements[object_number]['position']
            y += self.distance
            self.drive.drive_path([], (x, y), self.angle,  end_speed=-5, blocking=False)
            self.wait_for_task(can.MsgTypes.Popcorn_Command.value+1)
            self.drive.request_stop()
            self.wait_for_task(can.MsgTypes.Popcorn_Command.value+1)
            self.drive.drive_path([], self.my_game_elements[object_number]['start_position'], self.angle,  end_speed=5)
        else:
            object_number -= 2
            self.send_task_command(can.MsgTypes.Popcorn_Command.value, self.command['ready collect'], blocking=False)
            x, y = self.enemy_game_elements[object_number]['position']
            y += self.distance
            self.drive.drive_path([], (x, y), self.angle,  end_speed=-5, blocking=False)
            self.wait_for_task(can.MsgTypes.Popcorn_Command.value+1)
            self.drive.request_stop()
            self.wait_for_task(can.MsgTypes.Popcorn_Command.value+1)
            self.drive.drive_path([], self.enemy_game_elements[object_number]['start_position'], self.angle,  end_speed=5)

    def goto_empty(self):
        """ returns the position information of the place to empty the popcorn

        :return: position with angle
        """
        return self.empty_position['start_position']

    def do_empty(self):
        """ puts down the collected popcorn

        :return: None
        """
        self.drive.drive_path([], self.empty_position['position'], None, end_speed=-15)
        self.send_task_command(can.MsgTypes.Popcorn_Command.value, self.command['open case'], blocking=True)
        self.drive.drive_path([], self.empty_position['start_position'], None, end_speed=15)