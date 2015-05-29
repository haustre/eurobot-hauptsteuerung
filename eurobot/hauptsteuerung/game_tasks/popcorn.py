__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"


import time
import copy
from libraries import can
from hauptsteuerung.game_tasks.game_task import Task

class PopcornTask(Task):
    """ Class for collecting the popcorn from the popcorn machine """
    def __init__(self, robots, my_color, can_socket, drive):
        super().__init__(robots, can_socket, can.MsgTypes.Popcorn_Command.value, drive)
        self.calibrated = False
        self.angle = 90
        self.distance = 110
        empty_position = {'start_position': (800, 1000, 0), 'stands_position': (320, 1000, 0),
                          'popcorn_position': (180, 1000, 0)}
        self.command = {'ready collect': 0, 'open case': 1, 'collect': 2}
        popcorn_left = [{'start_position': (300, 420), 'position': (300, 0)},
                        {'start_position': (600, 420), 'position': (600, 0)}
                        ]
        self.calibration_point = [100, popcorn_left[0]['start_position'][1]]
        self.calibration_value = 149

        for popcorn in popcorn_left:
            popcorn['moved'] = False

        popcorn_right = copy.deepcopy(popcorn_left)
        for popcorn in popcorn_right:
            x, y = popcorn['start_position']
            popcorn['start_position'] = (3000 - x, y)
            x, y = popcorn['position']
            popcorn['position'] = (3000 - x, y)
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
            x, y, angle = empty_position['stands_position']
            self.empty_position['stands_position'] = 3000 - x, y, 180
            x, y, angle = empty_position['popcorn_position']
            self.empty_position['popcorn_position'] = 3000 - x, y, 180
            self.calibration_value = 3000 - self.calibration_value
            self.calibration_point[0] = 3000 - self.calibration_point[0]
        else:
            raise Exception("Unknown team color")

    def goto_task(self, object_number):
        """ returns the position information of the specified popcorn machine

        :param object_number: specifies which game element is chosen
        :return: position, angle
        """
        return self.my_game_elements[object_number]['kjskd'
                                                    ''
                                                    'sld'
                                                    'sheösëhvie¨s'
                                                    'ejslllehs'
                                                    'de'
                                                    'ehfie'
                                                    ''
                                                    'kdt_pofkd'
                                                    'fjrhdr'
                                                    'djjfurkffir73od'
                                                    'fdlrjdlr'
                                                    'fjrfhdlfjksition'], None

    def do_task(self, object_number):
        """ collecting the popcorn from the chosen popcorn machine
        """
        if self.calibrated is False:
            self.drive.enable_detection(False)
            self.drive.drive_path([], self.calibration_point, None,  end_speed=-21)
            x, y = self.robots['me'].get_position()
            offset = self.calibration_value - x
            print("Offset: " + str(offset))
            if abs(offset) < 500:
                self.drive.set_offset_x(offset)
                self.calibrated = True
            else:
                print("Calibration failed")
                self.my_game_elements[0]['moved'] = True
                self.my_game_elements[1]['moved'] = True
                self.drive.enable_detection(True)
                return
            self.drive.enable_detection(True)
            while self.drive.drive_path([], self.my_game_elements[object_number]['start_position'], None) is False:
                pass

        if self.calibrated is True:
            self.drive.enable_detection(False)
            self.send_task_command(can.MsgTypes.Popcorn_Command.value, self.command['ready collect'], blocking=False)
            x, y = self.my_game_elements[object_number]['position']
            y += self.distance
            path_point = x, y + 80
            self.drive.drive_path([path_point], (x, y), self.angle, path_speed=-20, end_speed=-5, blocking=True)
            # self.wait_for_task(can.MsgTypes.Popcorn_Command.value+1)
            # self.drive.request_stop()
            self.send_task_command(can.MsgTypes.Popcorn_Command.value, self.command['collect'], blocking=True)
            self.drive.enable_detection(True)
            while self.drive.drive_path([], self.my_game_elements[object_number]['start_position'], None) is False:
                pass
            self.my_game_elements[object_number]['moved'] = True

    def goto_empty(self):
        """ returns the position information of the place to empty the popcorn

        :return: position with angle
        """
        return self.empty_position['start_position'], None

    def do_empty(self):
        """ puts down the collected popcorn

        :return: None
        """
        self.drive.enable_detection(False)
        self.drive.drive_path([], self.empty_position['stands_position'], None, end_speed=-30)

        commands_other_tasks = {'cup left': 5, 'cup right': 6, 'stand': 3}
        self.send_task_command(can.MsgTypes.Cup_Command.value, commands_other_tasks['cup left'], blocking=False)
        self.send_task_command(can.MsgTypes.Cup_Command.value, commands_other_tasks['cup right'], blocking=False)
        self.send_task_command(can.MsgTypes.Stands_Command.value, commands_other_tasks['stand'], blocking=False)
        time.sleep(1.5)
        self.drive.drive_path([], self.empty_position['popcorn_position'], None, end_speed=-30)
        self.send_task_command(can.MsgTypes.Popcorn_Command.value, self.command['open case'], blocking=False)
        angle = self.empty_position['popcorn_position'][2]
        for _ in range(5):
            for rotation in (-4, 4):
                self.drive.drive_path([], None, angle + rotation)
        self.drive.enable_detection(True)
        self.drive.request_stop()
