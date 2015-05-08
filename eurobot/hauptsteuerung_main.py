"""
This is the main file to execute the software of the Beaglebone.
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import sys
import time
import socket
import queue
import subprocess
from libraries import can
from hauptsteuerung import drive
from hauptsteuerung import debug
from hauptsteuerung import game_tasks
from hauptsteuerung.robot import PositionMyRobot, PositionOtherRobot
from hauptsteuerung.game_logic import GameLogic


class Main():
    """ Main program running on Robot"""
    def __init__(self):
        """ In the initialisation the program determines on which robot it is running, reads in the configuration
        and creates all necessary objects.

        :return: None
        """
        self.debug = False  # False = running on the Robot, True F running on the PC
        hostname = socket.gethostname()
        if len(sys.argv) == 3:  # give 3 arguments for running on the Pc
            can_connection = sys.argv[1]
            hostname = sys.argv[2]
            self.debug = True
        else:   # running on the robot
            can_connection = 'can0'
            if not (hostname == 'Roboter-klein' or hostname == 'Roboter-gross'):
                raise Exception('Wrong Hostname\nSet Hostname to "Roboter-klein" or "Roboter-gross"')
        self.can_socket = can.Can(can_connection, can.MsgSender.Hauptsteuerung)
        if self.debug:
            self.enemy_simulation = debug.EnemySimulation(self.can_socket,  4, 20)
            self.enemy_simulation.start()
        else:
            self.clear_config('/root/gui_config')   # delete the old configuration file
            subprocess.Popen(['software/robo_gui'])     # start the GUI program
        self.countdown = game_tasks.Countdown(self.can_socket)
        self.debugger = debug.LaptopCommunication(self.can_socket)
        self.drive = drive.Drive(self.can_socket)
        self.reset = False
        self.debugger.start_can()
        self. strategy = self.read_config('/root/gui_config')
        self.strategy['robot_name'] = hostname
        print(self.strategy)
        self.send_start_configuration()
        self.robots = {'me': None, 'friendly robot': None, 'enemy1': None, 'enemy2': None}  # create the robot dictionary
        # create all game element objects
        self.game_tasks = \
            {'clapper': game_tasks.ClapperTask(self.robots, self.strategy['side'], self.can_socket, self.drive),
             'stair': game_tasks.StairTask(self.robots, self.strategy['side'], self.can_socket, self.drive),
             'stand': game_tasks.StandsTask(self.robots, self.strategy['side'], self.can_socket, self.drive),
             'cup': game_tasks.CupTask(self.robots, self.strategy['side'], self.can_socket, self.drive),
             'popcorn': game_tasks.PopcornTask(self.robots, self.strategy['side'], self.can_socket, self.drive)
             }
        self.game_logic = GameLogic(self.game_tasks, self.drive, self.countdown, self.robots)
        self.debugger.add_game_tasks(self.game_tasks)
        self.debugger.start_game_tasks()
        # create all robot objects and put them in a dictionary
        if self.strategy['robot_name'] == 'Roboter-klein':
            self.robots['me'] = PositionMyRobot(self.can_socket, can.MsgTypes.Position_Robot_small.value, self.strategy['robot_name'])
            if self.strategy['robot_big']:
                self.robots['friendly robot'] = PositionOtherRobot(self.can_socket, can.MsgTypes.Position_Robot_big.value)
        elif self.strategy['robot_name'] == 'Roboter-gross':
            self.robots['me'] = PositionMyRobot(self.can_socket, can.MsgTypes.Position_Robot_big.value, self.strategy['robot_name'])
            if self.strategy['robot_small']:
                self.robots['friendly robot'] = PositionOtherRobot(self.can_socket, can.MsgTypes.Position_Robot_small.value)
        else:
            raise Exception("Wrong Robot name")
        if self.strategy['enemy_small']:
            self.robots['enemy1'] = PositionOtherRobot(self.can_socket, can.MsgTypes.Position_Enemy_small.value)
        if self.strategy['robot_big']:
            self.robots['enemy2'] = PositionOtherRobot(self.can_socket, can.MsgTypes.Position_Enemy_big.value)
        self.drive.add_my_robot(self.robots['me'])
        for name, robot in self.robots.items():
            if robot is not None and name != 'me':
                self.drive.add_robot(robot)
        self.run()  # The configuration is complete. Start the game.

    def clear_config(self, file_name):
        """ deletes a given file

        :param file_name: name of the file to delete
        :type file_name: str
        :return: None
        """
        try:
            open(file_name, 'w').close()
        except FileNotFoundError:
            print('Configuration not found')

    def read_config(self, file_name):
        """ wait for the GUI program to write the config file and read it in

        :param file_name: name of the configuration file
        :type file_name: str
        :return: configuration dictionary
        """
        if self.debug:
            strategy = {
                'robot_small': True, 'robot_big': True, 'enemy_small': True, 'enemy_big': True,
                'robot_name': None, 'side': 'left', 'strategy': 0
            }
            print("!!!! Debug Program !!!!")
            return strategy
        else:
            while True:
                strategy = {}
                try:
                    with open(file_name) as f:
                        file_content = f.readlines()
                except FileNotFoundError:
                    print('Configuration not found')
                if len(file_content) == 7:
                    complete = file_content[6].strip().strip('complete: ')
                    if complete == 'yes':
                        strategy['side'] = file_content[0].strip().strip('side: ')
                        strategy['strategy'] = file_content[1].strip().strip('strategy: ')
                        strategy['enemy_small'] = file_content[2].strip().strip('enemy small: ')
                        strategy['enemy_big'] = file_content[3].strip().strip('enemy big: ')
                        strategy['robot_small'] = file_content[4].strip().strip('own_robot_small: ')
                        strategy['robot_big'] = file_content[5].strip().strip('own_robot_big: ')
                        return strategy
                else:
                    print('Configuration not finished')
                    time.sleep(0.5)

    def send_start_configuration(self):
        """ sends the configuration over CAN to the other boards

        :return: None
        """
        if self.strategy['side'] == 'left':
            side = 1
        else:
            side = 0
        if self.strategy['strategy'] == 'C' and False:
            start_orientation = 0   # near Clapper
        else:
            start_orientation = 1   # near Stair
        can_msg = {
            'type': can.MsgTypes.Configuration.value,
            'is_robot_small': self.strategy['robot_small'],
            'is_robot_big': self.strategy['robot_big'],
            'is_enemy_small': self.strategy['enemy_small'],
            'is_enemy_big': self.strategy['enemy_big'],
            'start_left': side,
            'start_orientation': start_orientation,
            'reserve': 0
        }
        self.can_socket.send(can_msg)

    def run(self):
        """ starts the game

        :return: None
        """
        self.wait_for_game_start()  # start of the game (key removed, emergency stop not pressed)
        self.countdown.start()
        self.can_socket.create_interrupt(can.MsgTypes.Peripherie_inputs.value, self.periphery_input)
        self.countdown.set_interrupt(self.game_end, 'game_end', 3)
        self.strategy_start()  # run the start strategy
        print("Programm End")

    def wait_for_game_start(self):
        """ wait for the start of the game ( key removed )

        :return: None
        """
        peripherie_queue = queue.Queue()
        queue_number = self.can_socket.create_queue(can.MsgTypes.Peripherie_inputs.value, peripherie_queue)
        game_started = False
        while game_started is False:
            peripherie_msg = peripherie_queue.get()
            if peripherie_msg['key_inserted'] == 0:
                game_started = True
        self.can_socket.remove_queue(queue_number)

    def periphery_input(self, can_msg):
        """ checks inputs of the periphery board
        sets the reset flag if the emergency key is pressed

        :return: None
        """
        if can_msg['emergency_stop'] == 1 and can_msg['key_inserted'] == 0 and False:  # TODO: activate
            can_msg = {
                'type': can.MsgTypes.EmergencyShutdown.value,
                'code': 0,
            }
            self.can_socket.send(can_msg)
            print("Emergency stop")
            self.reset = True

    def game_end(self, time_string):
        """ This method is called at the end of the game.
        It sends a emergency stop message over Can to ensure that nothing moves after the game end.

        :param time_string: name of the interrupt
        :return: None
        """
        if time_string is 'game_end':
            can_msg = {
                'type': can.MsgTypes.EmergencyShutdown.value,
                'code': 0,
            }
            self.can_socket.send(can_msg)
            self.game_logic.stop()
            time.sleep(2)  # TODO: make longer
            print("Game End")
            self.reset = True
            time.sleep(0.5)
            sys.exit()

    def strategy_start(self):  # TODO: Contains multiple test scenarios which will be removed
        """ Executes the chosen start strategy

        :return: None
        """
        if self.strategy['robot_name'] == 'Roboter-gross':  # check on which robot the program is running
            if self.strategy['strategy'] == 'A':
                if True:
                    self.drive.set_close_range_detection(True)
                    self.drive.set_enemy_detection(True)
                    self.drive.set_speed(15)
                    self.game_tasks['stand'].do_task(3)
                    self.game_tasks['stand'].do_task(4)
                    self.game_tasks['stand'].goto_task(1)
                    self.game_tasks['stand'].do_task(1)
                    self.drive.drive_path([], (1000, 1000), None)
                    point = self.game_tasks['stand'].goto_empty()
                    self.drive.drive_route(point, None)
                    self.game_tasks['stand'].do_empty()
                    self.drive.drive_path([], (1000, 1000), None)
                if False:
                    point, angle = self.game_tasks['popcorn'].goto_task(0)
                    self.drive.drive_route(point, angle)
                    self.game_tasks['popcorn'].do_task(0)
                    point, angle = self.game_tasks['popcorn'].goto_task(1)
                    self.drive.drive_route(point, angle)
                    self.game_tasks['popcorn'].do_task(1)
                    point = self.game_tasks['popcorn'].goto_empty()
                    self.drive.drive_route(point, None)
                    self.game_tasks['popcorn'].do_empty()
                if False:
                    point, angle = self.game_tasks['clapper'].goto_task(1)
                    self.drive.drive_route(point, angle)
                    self.game_tasks['clapper'].do_task(1)
                    self.drive.drive_path([], (1000, 1000), None)

            elif self.strategy['strategy'] == 'B':
                self.drive.set_close_range_detection(False)
                self.drive.set_enemy_detection(False)
                self.drive.set_speed(30)
                self.drive.drive_path([], (1000, 1000), None)
                point, angle = self.game_tasks['popcorn'].goto_task(0)
                self.drive.drive_route(point, angle)
                self.game_tasks['popcorn'].do_task(0)
                point, angle = self.game_tasks['popcorn'].goto_task(1)
                self.drive.drive_route(point, angle)
                self.game_tasks['popcorn'].do_task(1)
                point = self.game_tasks['popcorn'].goto_empty()
                self.drive.drive_route(point, None)
                self.game_tasks['popcorn'].do_empty()
            elif self.strategy['strategy'] == 'C':  # Test strategy
                if False:
                    self.drive.set_close_range_detection(True)
                    self.drive.set_enemy_detection(True)
                    self.drive.set_speed(30)
                    self.drive.drive_path([], (800, 1000), None)
                    while self.reset is False:
                        points = [(900, 1400), (2100, 900), (900, 900), (2100, 1400)]
                        for point in points:
                            for i in range(1):
                                self.drive.drive_route(point, None, timeout=20)
                if True:
                    self.drive.set_close_range_detection(True)
                    self.drive.set_enemy_detection(True)
                    self.drive.set_speed(40)
                    #if self.strategy['side'] == 'left':
                    #    self.drive.drive_path([], (800, 1000), None)
                    #else:
                    #    self.drive.drive_path([], (3000-800, 1000), None)
                    self.game_tasks['stand'].do_task(3)
                    self.game_logic.start()
                    time.sleep(60)
                    self.game_logic.stop()

        if self.strategy['robot_name'] == 'Roboter-klein':
            time.sleep(3)
            if self.strategy['strategy'] == 'A':
                self.drive.set_close_range_detection(False)
                self.drive.set_enemy_detection(False)

                self.drive.set_speed(100)
                if self.strategy['side'] == 'left':
                    self.drive.drive_path([], (500, 1080), None)
                else:
                    self.drive.drive_path([], (3000-500, 1080), None)

                self.drive.set_close_range_detection(True)
                self.drive.set_enemy_detection(True)

                point, angle = self.game_tasks['stair'].goto_task()

                if self.strategy['side'] == 'left':
                    if self.drive.drive_path([],(1250, 1080), angle) == False:
                        time.sleep(1)
                        self.drive.drive_path([],(1250, 1080), angle)
                    while self.drive.drive_path([],point, angle) == False:
                         print("Waiting")
                         time.sleep(1)
                else:
                    if self.drive.drive_path([],(3000-1250, 1080), angle) == False:
                        time.sleep(1)
                        self.drive.drive_path([],(3000-1250, 1080), angle)
                    while self.drive.drive_path([],point, angle) == False:
                        print("Waiting")
                        time.sleep(1)

                print("Do Climbing Task")
                self.drive.set_close_range_detection(False)
                self.drive.set_enemy_detection(False)
                self.drive.set_speed(60)
                self.game_tasks['stair'].do_task()

            elif self.strategy['strategy'] == 'B':
                raise Exception('Strategy not programmed')
            elif self.strategy['strategy'] == 'C':  # Test strategy
                raise Exception('Strategy not programmed')


if __name__ == "__main__":
    while True:
        main_program = Main()
        print("Robot Resets")