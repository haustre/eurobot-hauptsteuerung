__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"


import threading
import time
from libraries import can
from hauptsteuerung.game_tasks.game_task import Task

class StairTask(Task):
    """ Class for driving to the top of the stair """
    def __init__(self, robots, my_color, can_socket, drive):
        super().__init__(robots, can_socket, can.MsgTypes.Climbing_Command.value, drive)
        self.climbing_command = {'up': 0, 'bottom': 1, 'middle': 2, 'top': 3}
        self.carpet_command = {'fire right': 0, 'fire left': 1}
        path_left = {'in_front': (1240, 740, 270),
                     'bottom': (1240, 700, 270),
                     'beginning': (1240, 650, 270),
                     'top': (1240, 200, 270),
                     'top not reached': (1240, 220, 270),
                     'carpet 1': (1100, 240, 185),
                     'fire 1': self.carpet_command['fire left'],
                     'turning point1': (1190, 220, 270),
                     'turning point2': (1330, 220, 270),
                     'carpet 2': (1380, 240, 355),
                     'fire 2': self.carpet_command['fire right'],
                     'end point': (1240, 210, 90)
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
        path_right['carpet 1'] = x, y, 360 - (angle - 180)
        x, y, angle = path_right['carpet 2']
        path_right['carpet 2'] = x, y, 360 - (angle - 180)
        # fire1 = path_right['fire 1']
        # fire2 = path_right['fire 2']
        # path_right['fire 1'] = fire2
        # path_right['fire 2'] = fire1

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
        self.drive.set_speed(40)
        self.send_task_command(can.MsgTypes.Climbing_Command.value, self.climbing_command['bottom'], blocking=True)
        timer = threading.Timer(1.5, self.send_climbing_middle)
        timer.setDaemon(True)
        timer.start()
        timer2 = threading.Timer(4.5, self.send_climbing_top)
        timer2.setDaemon(True)
        timer2.start()
        self.drive.drive_path([], self.my_path['top'], None)

        myX, myY = self.robots['me'].get_position()

        while myY > 290:
            self.drive.drive_path([], self.my_path['top not reached'], None)
            myY, myY = self.robots['me'].get_position()

        self.drive.set_speed(60)
        self.send_task_command(can.MsgTypes.Climbing_Command.value, self.climbing_command['up'], blocking=False)
        time.sleep(3)
        self.drive.drive_path([], self.my_path['carpet 1'], None)
        self.send_task_command(can.MsgTypes.Carpet_Command.value, self.my_path['fire 1'], blocking=True)
        self.drive.drive_path([], self.my_path['turning point1'], None, end_speed=(-self.drive.speed))
        self.drive.drive_path([], self.my_path['carpet 2'], None)
        self.send_task_command(can.MsgTypes.Carpet_Command.value, self.my_path['fire 2'], blocking=True)
        self.drive.drive_path([], self.my_path['turning point2'], None, end_speed=(-self.drive.speed))
        self.drive.drive_path([], self.my_path['end point'], None, end_speed=(-self.drive.speed))

    def send_climbing_middle(self):
        self.send_task_command(can.MsgTypes.Climbing_Command.value, self.climbing_command['middle'])


    def send_climbing_top(self):
        self.send_task_command(can.MsgTypes.Climbing_Command.value, self.climbing_command['top'])

    def prepare_for_climbing(self):
        self.send_task_command(can.MsgTypes.Climbing_Command.value, self.climbing_command['bottom'], blocking=False)
