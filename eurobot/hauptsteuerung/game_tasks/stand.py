__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import time
import math
import copy
from libraries import can
from hauptsteuerung.game_tasks.game_task import Task

class StandsTask(Task):
    """ Class collecting the stands """
    def __init__(self, robots, my_color, can_socket, drive):
        super().__init__(robots, can_socket, can.MsgTypes.Stands_Command.value, drive)
        self.distance_to_stand = 200
        self.special_cup = 0
        empty_position = {'start_position': (1250, 1620, 90), 'position': (1250, 1770, 90)}
        self.command = {'blocked': 0, 'ready collect': 1, 'ready platform': 2, 'open case': 3}
        self.commandCup = {'blocked': 0, 'ready collect left': 1, 'ready collect right': 2, 'collect left': 3,
                           'collect right': 4, 'open case left': 5, 'open case right': 6, 'close case left': 7,
                           'close case right': 8}
        stands_left = [{'position': (90, 200), 'start position': (300, 490), 'end position': (230, 490)},
                       {'position': (90, 1750), 'start position': (300, 1460), 'end position': (230, 1500)},
                       {'position': (850, 200), 'start position': (650, 490), 'end position': (660, 300)},
                       {'position': (870, 1355), 'start position': None, 'end position': None},
                       {'position': (1100, 1770), 'start position': None, 'end position': None},
                       {'position': (1300, 1400), 'start position': None, 'end position': None},
                       ]

        self.second_stands = [{'position': (90, 1850), 'start position': None},
                              {'position': (850, 100), 'start position': None},
                              ]

        for stand in stands_left:
            stand['moved'] = False

        stands_right = copy.deepcopy(stands_left)
        for stand in stands_right:
            x, y = stand['position']
            stand['position'] = (3000 - x, y)
            if stand['start position'] is not None:
                x, y = stand['start position']
                stand['start position'] = (3000 - x, y)
                x, y = stand['end position']
                stand['end position'] = (3000 - x, y)
        if my_color == 'left':
            self.my_game_elements = stands_left
            self.enemy_game_elements = stands_right
            self.empty_position = empty_position
            self.side = 'left'
            self.angleStandStair = 180

        elif my_color == 'right':
            self.empty_position = {}
            self.my_game_elements = stands_right
            self.enemy_game_elements = stands_left
            x, y, angle = empty_position['start_position']
            self.empty_position['start_position'] = 3000 - x, y, angle
            x, y, angle = empty_position['position']
            self.empty_position['position'] = 3000 - x, y, angle
            x, y = self.second_stands[0]['position']
            self.second_stands[0]['position'] = 3000 - x, y
            x, y = self.second_stands[1]['position']
            self.second_stands[1]['position'] = 3000 - x, y
            self.angleStandStair = 0

            self.side = 'right'
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
        if object_number == 0 or object_number == 1 or object_number == 2:
            self.drive.enable_detection(False)
        starting_point = self.robots['me'].get_position()
        stand_point = self.my_game_elements[object_number]['position']
        self.send_task_command(can.MsgTypes.Stands_Command.value, self.command['ready collect'])
        point1 = self.calculate_stopping_point(starting_point, stand_point, 30)
        point2 = self.calculate_stopping_point(starting_point, stand_point, -70)
        self.drive.drive_path([point1[0:2]], point2[0:2], None, end_speed=10)

        if object_number == 0:
            time.sleep(0.5)
        if object_number == 1:
            time.sleep(0.5)
            if self.side == 'left':
                self.drive.drive_path([], None, 45)
            else:
                self.drive.drive_path([], None, 180-45)
        elif object_number == 2:
            time.sleep(0.5)
            if self.side == 'left':
                self.drive.drive_path([], None, 225)
            else:
                self.drive.drive_path([], None, 315)

        self.my_game_elements[object_number]['moved'] = True
        self.drive.enable_detection(True)

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
        return self.empty_position['start_position'], None

    def do_empty(self):
        """ puts down the stands """
        self.drive.enable_detection(False)
        self.send_task_command(can.MsgTypes.Stands_Command.value, self.command['ready platform'], blocking=True)
        self.drive.drive_path([], self.empty_position['position'], None, end_speed=25)
        self.send_task_command(can.MsgTypes.Stands_Command.value, self.command['open case'], blocking=True)
        self.drive.drive_path([], self.empty_position['start_position'], None, end_speed=-25)
        self.send_task_command(can.MsgTypes.Stands_Command.value, self.command['ready collect'])
        self.send_task_command(can.MsgTypes.Stands_Command.value, self.command['blocked'])
        time.sleep(0.5)
        self.drive.enable_detection(True)
