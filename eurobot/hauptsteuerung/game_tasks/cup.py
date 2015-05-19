__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"


import time
import math
from libraries import can
from hauptsteuerung.game_tasks.game_task import Task

class CupTask(Task):
    """ Class collecting the cups """
    def __init__(self, robots, my_color, can_socket, drive):
        super().__init__(robots, can_socket, can.MsgTypes.Cup_Command.value, drive)
        self.my_color = my_color
        self.distance = 150
        self.shift = 120
        self.free_arms = {'right': True, 'left': True}
        self.command = {'blocked': 0, 'ready collect left': 1, 'ready collect right': 2, 'collect left': 3,
                        'collect right': 4, 'open case left': 5, 'open case right': 6, 'close case left': 7,
                        'close case right': 8}

        cups_left = [{'position': (250, 1750), 'pick up side': 'left'},
                     {'position': (910, 830), 'pick up side': 'left'},
                     {'position': (1500, 1650), 'pick up side': 'right'},
                     {'position': (2090, 830), 'pick up side': 'left'},
                     {'position': (2750, 1750), 'pick up side': 'right'}
                     ]

        for stand in cups_left:
            stand['moved'] = False
        self.my_game_elements = cups_left

    def goto_task(self, object_number):
        """ returns the position information of the specified cup

        :param object_number: specifies which game element is chosen
        :return: position, angle
        """
        return (670, 1300), None  # TODO: set correct position

    def do_task(self, object_number):
        """ collects the chosen cup

        :param object_number:  specifies which game element is chosen
        """
        starting_point = self.robots['me'].get_position()
        stand_point = self.my_game_elements[object_number]['position']

        self.make_ready_for_cup(object_number)
        point1, point2, angle = self.calculate_stopping_points(starting_point, stand_point, object_number)
        self.drive.drive_path([point1], point2, angle, end_speed=10)
        self.take_cup(object_number)
        self.my_game_elements[object_number]['moved'] = True
        time.sleep(0.2)

    def make_ready_for_cup(self, object_number):
        if self.my_game_elements[object_number]['pick up side'] == 'left':
            self.send_task_command(can.MsgTypes.Cup_Command.value, self.command['ready collect left'])
        else:
            self.send_task_command(can.MsgTypes.Cup_Command.value, self.command['ready collect right'])

    def take_cup(self, object_number):
        if self.my_game_elements[object_number]['pick up side'] == 'left':
            self.send_task_command(can.MsgTypes.Cup_Command.value, self.command['collect left'])
        else:
            self.send_task_command(can.MsgTypes.Cup_Command.value, self.command['collect right'])

    def release_cup(self):
        self.send_task_command(can.MsgTypes.Cup_Command.value, self.command['open case left'])
        self.send_task_command(can.MsgTypes.Cup_Command.value, self.command['open case right'])

    def close_case(self):
        self.send_task_command(can.MsgTypes.Cup_Command.value, self.command['close case left'])
        self.send_task_command(can.MsgTypes.Cup_Command.value, self.command['close case right'])

    def calculate_stopping_points(self, from_pos, to_pos, object_number):
        """ calculates the correct position to collect the cup

        :param from_pos: position of the robot
        :param to_pos: position of the stand
        :param object_number: specifies which game element is chosen
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

        if self.my_game_elements[object_number]['pick up side'] == 'left':
            x = math.cos(angle - math.pi / 2) * self.shift
            y = math.sin(angle - math.pi / 2) * self.shift
        else:
            x = math.cos(angle + math.pi / 2) * self.shift
            y = math.sin(angle + math.pi / 2) * self.shift
        point1[0] = int(point1[0] - x)
        point1[1] = int(point1[1] - y)

        x = math.cos(angle) * 50
        y = math.sin(angle) * 50
        point2[0] = int(point1[0] + x)
        point2[1] = int(point1[1] + y)
        return point1, (point2[0], point2[1]), angle / (2 * math.pi) * 360
