"""
This is the main file to execute the software of the Beaglebone.
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import sys
import time
import socket
import queue
import math
import gc
import datetime

from libraries import can
from libraries.start_text import print_start_text
from hauptsteuerung.beaglebone import GPIO
from hauptsteuerung import drive
from hauptsteuerung import debug
from hauptsteuerung import countdown
from hauptsteuerung.game_tasks import clapper, stair, stand, cup, popcorn
from hauptsteuerung.robot import PositionMyRobot, PositionOtherRobot
from hauptsteuerung.game_logic import GameLogic


class Main:
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
        self.gpio = GPIO()
        if self.debug:
            self.enemy_simulation = debug.EnemySimulation(self.can_socket,  4, 20)
            #self.enemy_simulation.start()
        self.countdown = countdown.Countdown(self.can_socket)
        self.debugger = debug.LaptopCommunication(self.can_socket)
        self.drive = drive.Drive(self.can_socket)
        self.reset = False
        self.debugger.start_can()
        self.strategy = self.read_config('/root/gui_config')
        self.strategy['robot_name'] = hostname
        print(self.strategy)
        self.send_start_configuration()
        self.robots = {'me': None, 'friendly robot': None, 'enemy1': None, 'enemy2': None}  # create the robot dictionary
        # create all game element objects
        self.game_tasks = \
            {'clapper': clapper.ClapperTask(self.robots, self.strategy['side'], self.can_socket, self.drive),
             'stair': stair.StairTask(self.robots, self.strategy['side'], self.can_socket, self.drive),
             'stand': stand.StandsTask(self.robots, self.strategy['side'], self.can_socket, self.drive),
             'cup': cup.CupTask(self.robots, self.strategy['side'], self.can_socket, self.drive),
             'popcorn': popcorn.PopcornTask(self.robots, self.strategy['side'], self.can_socket, self.drive)
             }
        self.game_logic = GameLogic(self.game_tasks, self.drive, self.countdown, self.robots, self.strategy['side'])
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
            if robot is not None and not(name == 'me' or name == 'friendly robot'):
                self.drive.add_robot(robot)
        self.run()  # The configuration is complete. Start the game.

    def read_config(self, file_name):
        """ wait for the GUI program to write the config file and read it in

        :param file_name: name of the configuration file
        :type file_name: str
        :return: configuration dictionary
        """
        print('Waiting for Configuration')
        strategy = {
            'robot_small': True, 'robot_big': True, 'enemy_small': True, 'enemy_big': True,
            'robot_name': None, 'side': 'left', 'strategy': 'A'
        }
        if self.debug:
            print("!!!! Debug Program !!!!")
            return strategy
        else:
            self.gpio.set_led(0, 1)
            self.gpio.set_led(1, 0)
            self.gpio.set_led(2, 1)
            self.gpio.set_led(3, 0)
            while self.gpio.get_button(4) == 0:  # Start not pressed
                if self.gpio.get_button(0):
                    strategy['side'] = 'left'
                    self.gpio.set_led(0, 1)
                    self.gpio.set_led(1, 0)
                elif self.gpio.get_button(1):
                    strategy['side'] = 'right'
                    self.gpio.set_led(0, 0)
                    self.gpio.set_led(1, 1)

                if self.gpio.get_button(2):
                    strategy['strategy'] = 'A'
                    self.gpio.set_led(2, 1)
                    self.gpio.set_led(3, 0)
                elif self.gpio.get_button(3):
                    strategy['strategy'] = 'B'
                    self.gpio.set_led(2, 0)
                    self.gpio.set_led(3, 1)
        self.gpio.blink_led()
        return strategy

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
        time.sleep(0.02)    # wait for gyro
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
        if can_msg['emergency_stop'] == 1 and can_msg['key_inserted'] == 0 and self.countdown.running is True:
            can_msg = {
                'type': can.MsgTypes.EmergencyShutdown.value,
                'code': 0,
            }
            self.can_socket.send(can_msg)
            print("Emergency stop")
            self.reset = True
            self.game_end('game_end')

    def game_end(self, time_string):
        """ This method is called at the end of the game.
        It sends a emergency stop message over Can to ensure that nothing moves after the game end.

        :param time_string: name of the interrupt
        :return: None
        """
        if time_string is 'game_end':
            self.reset = True
            self.game_logic.stop()
            self.drive.turn_off()
            self.countdown.stop()
            try:
                self.debugger.stop()
            except:
                print("Debugger not closed correctly")
            can_msg = {
                'type': can.MsgTypes.EmergencyShutdown.value,
                'code': 0,
            }
            self.can_socket.send(can_msg)
            time.sleep(2)  # TODO: make longer
            del self.drive
            del self.countdown
            del self.gpio
            del self.debugger
            del self.can_socket
            print("Game End")

    def strategy_start(self):  # TODO: Contains multiple test scenarios which will be removed
        """ Executes the chosen start strategy

        :return: None
        """
        if self.strategy['robot_name'] == 'Roboter-gross':  # check on which robot the program is running
            if self.strategy['strategy'] == 'A':
                self.drive.set_close_range_detection(True)
                self.drive.set_enemy_detection(True)
                self.drive.set_speed(40)
                self.game_tasks['stand'].do_task(3)
                self.game_logic.start()

            elif self.strategy['strategy'] == 'B':
                self.drive.set_close_range_detection(True)
                self.drive.set_enemy_detection(True)
                self.drive.set_speed(40)
                self.game_tasks['stand'].do_task(3)
                self.game_logic.start()

        if self.strategy['robot_name'] == 'Roboter-klein':
            # Wait until big robot is away
            time.sleep(1)

            # Check position side
            XOffset = 0
            if self.strategy['side'] == 'right':
                XOffset = 3000

            if self.strategy['strategy'] == 'A':
                # Ignore emeny in start area
                self.drive.set_close_range_detection(False)
                self.drive.set_enemy_detection(False)

                # Full speed
                self.drive.set_speed(100)

                # Drive out of the start area
                self.drive.drive_path([], (math.fabs(480-XOffset), 1060), None)

                # Pay attention for emenies
                self.drive.set_close_range_detection(True)
                self.drive.set_enemy_detection(True)

                # Side on wich the robot drives
                sideState = 0
                endPositionReached = False

                # Drive caterpillar down
                self.game_tasks['stair'].prepare_for_climbing()

                smallRobotTimeout = 10

                while endPositionReached == False:

                    # Drive on the left side ---------------------------------------------
                    if sideState == 0:
                        if self.drive.try_drive_path([],(math.fabs(1250 - XOffset), 1090), 270, smallRobotTimeout) == True:
                            endPositionReached = True

                        else:
                            sideState = 1

                    # Change to the right side -------------------------------------------
                    if sideState == 1:
                        # Ignore emeny only for turning
                        self.drive.set_close_range_detection(False)
                        self.drive.set_enemy_detection(False)
                        self.drive.drive_path([], None, 270)
                        self.drive.set_close_range_detection(True)
                        self.drive.set_enemy_detection(True)

                        # Get position
                        myX, myY = self.robots['me'].get_position()

                        # Change again to the left side, if enemy detected
                        if self.drive.try_drive_path([],(myX, 900), 180, smallRobotTimeout) == True:
                            sideState = 2
                        else:
                            sideState = 3


                    # Drive on the right side ---------------------------------------------
                    if sideState == 2:
                        if self.drive.try_drive_path([],(math.fabs(1250 - XOffset), 900), 270, smallRobotTimeout) == True:
                            endPositionReached = True

                        else:
                            sideState = 3

                    # Change to the left side -------------------------------------------
                    if sideState == 3:
                        # Ignore emeny only for turning
                        self.drive.set_close_range_detection(False)
                        self.drive.set_enemy_detection(False)
                        self.drive.drive_path([], None, 90)
                        self.drive.set_close_range_detection(True)
                        self.drive.set_enemy_detection(True)

                        # Get position
                        myX, myY = self.robots['me'].get_position()

                        # Change again to the right side, if enemy detected
                        if self.drive.try_drive_path([],(myX, 1090), 180,smallRobotTimeout) == True:
                            sideState = 1
                        else:
                            sideState = 2

                # Drive in front of the stair
                point, angle = self.game_tasks['stair'].goto_task()
                tryToDriveInFrontOfStair = 0

                while self.drive.try_drive_path([],point, angle, 1.5*smallRobotTimeout) == False:

                    # Drive back after timeout

                    # Get position
                    myX, myY = self.robots['me'].get_position()
                    # Drive back without enemy detection
                    self.drive.set_speed(-20)
                    self.drive.set_close_range_detection(False)
                    self.drive.set_enemy_detection(False)
                    self.drive.drive_path([],(math.fabs(1250 - XOffset), (myY + 60)), None)
                    self.drive.set_close_range_detection(True)
                    self.drive.set_enemy_detection(True)
                    self.drive.set_speed(100)

                # Climb on the stair without enemy detection
                print("Do Climbing Task")
                self.drive.set_close_range_detection(False)
                self.drive.set_enemy_detection(False)
                self.game_tasks['stair'].do_task()

            elif self.strategy['strategy'] == 'B':
                raise Exception('Strategy not programmed')


if __name__ == "__main__":
    time.sleep(1)
    print_start_text('Wall - e')
    print("Program starts: " + str(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")))
    main_program = Main()
    del main_program
    gc.collect()
    print("Program finished")


