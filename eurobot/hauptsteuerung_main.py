"""
This is the main file to execute the software of the Beaglebone.
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import sys
import os
import time
import socket
import threading
import queue
import math
import numpy as np
import subprocess
from libraries import can
from hauptsteuerung import drive
from hauptsteuerung import debug
from hauptsteuerung import game_logic
from hauptsteuerung.robot import PositionMyRobot, PositionOtherRobot


class Main():
    def __init__(self):
        """ Main programm running on Robot"""
        self.debug = False
        hostname = socket.gethostname()
        if len(sys.argv) == 3:
            can_connection = sys.argv[1]
            hostname = sys.argv[2]
            self.debug = True
        else:
            can_connection = 'can0'
            if not (hostname == 'Roboter-klein' or hostname == 'Roboter-gross'):
                raise Exception('Wrong Hostname\nSet Hostname to "Roboter-klein" or "Roboter-gross"')
        self.can_socket = can.Can(can_connection, can.MsgSender.Hauptsteuerung)
        if self.debug:
            self.enemy_simulation = debug.EnemySimulation(self.can_socket,  4, 20)
            self.enemy_simulation.start()
        else:
            self.clear_config('/root/gui_config')
            subprocess.Popen(['software/robo_gui'])
        self.countdown = game_logic.Countdown(self.can_socket)
        self.debugger = debug.LaptopCommunication(self.can_socket)
        self.drive = drive.Drive(self.can_socket)
        self.reset = False
        self.debugger.start_can()
        self. strategy = self.read_config('/root/gui_config')
        self.strategy['robot_name'] = hostname
        print(self.strategy)
        self.robots = {'me': None, 'friendly robot': None, 'enemy1': None, 'enemy2': None}
        self.game_tasks = \
            {'clapper': game_logic.ClapperTask(self.robots, self.strategy['side'], self.can_socket, self.drive),
             'stair': game_logic.StairTask(self.robots, self.strategy['side'], self.can_socket, self.drive),
             'stand': game_logic.StandsTask(self.robots, self.strategy['side'], self.can_socket, self.drive),
             'cup': game_logic.CupTask(self.robots, self.strategy['side'], self.can_socket, self.drive),
             'popcorn': game_logic.PopcornTask(self.robots, self.strategy['side'], self.can_socket, self.drive)
             }
        self.debugger.add_game_tasks(self.game_tasks)
        self.debugger.start_game_tasks()
        self.run()

    def clear_config(self, file_name):
        try:
            open(file_name, 'w').close()
        except FileNotFoundError:
            print('Configuration not found')

    def read_config(self, file_name):
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
                    time.sleep(2)

    def run(self):
        # TODO: get information from gui
        if self.strategy['side'] == 'left':
            side = 1
        else:
            side = 0
        if self.strategy['strategy'] == 1 or self.strategy['strategy'] == 2:
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
        if self.strategy['robot_name'] == 'Roboter-klein':
            #print("Robot small")
            self.robots['me'] = PositionMyRobot(self.can_socket, can.MsgTypes.Position_Robot_small.value, self.strategy['robot_name'])
            if self.strategy['robot_big']:
                self.robots['friendly robot'] = PositionOtherRobot(self.can_socket, can.MsgTypes.Position_Robot_big.value)
        elif self.strategy['robot_name'] == 'Roboter-gross':
            #print("Robot big")
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
        self.wait_for_game_start()  # start of the game (key removed, emergency stop not pressed)
        self.countdown.start()
        self.can_socket.create_interrupt(can.MsgTypes.Peripherie_inputs.value, self.periphery_input)
        self.countdown.set_interrupt(self.game_end, 'game_end', 2)
        self.strategy_start()
        print("Programm End")

    def wait_for_game_start(self):
        peripherie_queue = queue.Queue()
        queue_number = self.can_socket.create_queue(can.MsgTypes.Peripherie_inputs.value, peripherie_queue)
        game_started = False
        while game_started is False:
            peripherie_msg = peripherie_queue.get()
            if peripherie_msg['key_inserted'] == 0:
                game_started = True
        self.can_socket.remove_queue(queue_number)

    def periphery_input(self, can_msg):
        if can_msg['emergency_stop'] == 1 and can_msg['key_inserted'] == 0 and False:  # TODO: activate
            can_msg = {
                'type': can.MsgTypes.EmergencyShutdown.value,
                'code': 0,
            }
            self.can_socket.send(can_msg)
            print("Emergency stop")
            self.reset = True

    def game_end(self, time_string):
        if time_string is 'game_end':
            can_msg = {
                'type': can.MsgTypes.EmergencyShutdown.value,
                'code': 0,
            }
            self.can_socket.send(can_msg)
            time.sleep(5)  # TODO: make longer
            print("Game End")
            self.reset = True

    def strategy_start(self):
        if self.strategy['robot_name'] == 'Roboter-gross':
            if self.strategy['strategy'] == 'A':
                if True:
                    self.drive.set_close_range_detection(False)
                    self.drive.set_enemy_detection(False)
                    self.drive.set_speed(30)
                    self.game_tasks['stand'].do_task(5)
                    self.game_tasks['stand'].do_task(6)
                    self.drive.drive_path([], (290, 1460), None)
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
                if True:
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
            elif self.strategy['strategy'] == 'C':
                if True:
                    self.drive.set_close_range_detection(True)
                    self.drive.set_enemy_detection(True)
                    self.drive.set_speed(30)
                    self.drive.drive_path([], (800, 1000), None)
                    while self.reset is False:
                        points = [(900, 1400), (2100, 900), (900, 900), (2100, 1400)]
                        for point in points:
                            for i in range(1):
                                self.drive.drive_route(point, None, 180)
                if True:
                    self.drive.set_close_range_detection(False)
                    self.drive.set_enemy_detection(False)
                    self.drive.set_speed(15)
                    self.drive.drive_path([], (1000, 1000), 0)
                    point, angle = self.game_tasks['popcorn'].goto_task(0)
                    self.drive.drive_route(point, angle)
                    self.game_tasks['popcorn'].do_task(0)

                    point, angle = self.game_tasks['popcorn'].goto_task(1)
                    self.drive.drive_route(point, angle)
                    self.game_tasks['popcorn'].do_task(1)

                    self.drive.drive_route((2600, 400), 180)
                if False:
                    self.drive.set_close_range_detection(False)
                    self.drive.set_enemy_detection(False)
                    self.drive.set_speed(15)
                    self.drive.drive_path([], (1000, 1000), 0)
                    point, angle = self.game_tasks['clapper'].goto_task(1)
                    self.drive.drive_route(point, angle)
                    self.game_tasks['clapper'].do_task(1)

        if self.strategy['robot_name'] == 'Roboter-klein':
            if self.strategy['strategy'] == 'A':
                self.drive.set_close_range_detection(False)
                self.drive.set_enemy_detection(False)
                self.drive.set_speed(100)
                point, angle = self.game_tasks['stair'].goto_task()
                self.drive.drive_path([], point, angle)
                self.drive.set_close_range_detection(False)
                self.drive.set_speed(60)
                self.game_tasks['stair'].do_task()
            elif self.strategy['strategy'] == 'B':
                raise Exception('Strategy not programmed')
            elif self.strategy['strategy'] == 'C':
                raise Exception('Strategy not programmed')
if __name__ == "__main__":
    while True:
        main_program = Main()
        print("Robot Resets")