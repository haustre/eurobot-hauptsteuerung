__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

from libraries import can
from hauptsteuerung.game_tasks.game_task import Task

class ClapperTask(Task):
    """ Class for closing the clappers """
    def __init__(self, robots, my_color, can_socket, drive):
        super().__init__(robots, can_socket, can.MsgTypes.Clapper_Command.value, drive)
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
        if clapper_number == 0 and self.my_game_elements[1]['moved'] is False:
            self.do_both_clapper_fast()
        else:
            self.drive.enable_detection(False)
            side = self.my_game_elements[clapper_number]['side']
            self.send_task_command(can.MsgTypes.Clapper_Command.value, self.command[side], blocking=False)
            if side == 'right':
                angle = 0
            else:
                angle = 180
            self.drive.drive_path([], None, angle, end_speed=40)
            self.send_task_command(can.MsgTypes.Clapper_Command.value, self.command['up'])
            self.my_game_elements[clapper_number]['moved'] = True
            self.drive.enable_detection(True)

    def do_both_clapper_fast(self):
        # Close first clapper
        side = self.my_game_elements[0]['side']
        self.send_task_command(can.MsgTypes.Clapper_Command.value, self.command[side], blocking=True)
        if side == 'right':
            angle = 0
        else:
            angle = 180
        self.drive.drive_path([], None, angle, end_speed=40)
        self.send_task_command(can.MsgTypes.Clapper_Command.value, self.command['up'])
        self.my_game_elements[0]['moved'] = True

        # Drive to next clapper
        (x0, y0), angle0 = self.my_game_elements[0]['position'], self.angle
        (x1, y1), angle1 = self.my_game_elements[1]['position'], self.angle
        y0 -= self.distance
        y1 -= self.distance

        if self.drive.drive_path([], ((x0 + x1) / 2, y0), None):
            # Close second clapper
            self.send_task_command(can.MsgTypes.Clapper_Command.value, self.command[side], blocking=True)
            self.drive.drive_path([], (x1, y1), None)
            self.send_task_command(can.MsgTypes.Clapper_Command.value, self.command['up'])
            self.my_game_elements[1]['moved'] = True
