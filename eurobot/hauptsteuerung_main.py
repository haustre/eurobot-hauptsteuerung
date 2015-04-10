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
from libraries import can
from hauptsteuerung import debug
from hauptsteuerung import game_logic
from hauptsteuerung import route_finding
from hauptsteuerung.robot import PositionMyRobot, PositionOtherRobot


class Main():
    def __init__(self):
        """ Main programm running on Robot"""
        hostname = socket.gethostname()
        if len(sys.argv) == 3:
            can_connection = sys.argv[1]
            hostname = sys.argv[2]
        else:
            can_connection = 'can0'
            if not (hostname == 'Roboter-klein' or hostname == 'Roboter-gross'):
                raise Exception('Wrong Hostname\nSet Hostname to "Roboter-klein" or "Roboter-gross"')
        self.can_socket = can.Can(can_connection, can.MsgSender.Hauptsteuerung)
        self.countdown = game_logic.Countdown(self.can_socket)
        self.debugger = debug.LaptopCommunication(self.can_socket)
        self.route_finder = route_finding.RouteFinding(self.can_socket)
        self.enemy_simulation = debug.EnemySimulation(self.can_socket,  4, 20)
        self.reset = False
        self.strategy = {
            'robot_small': False, 'robot_big': True, 'enemy_small': False, 'enemy_big': False,
            'robot_name': hostname, 'side': 'right', 'strategy': 0
        }
        self.robots = {'me': None, 'friendly robot': None, 'enemy1': None, 'enemy2': None}

        self.game_tasks = {'clapper': game_logic.ClapperTask(self.robots, self.strategy['side'], self.can_socket),
                           'stair': game_logic.StairTask(self.robots, self.strategy['side'], self.can_socket),
                           'stand': game_logic.StandsTask(self.robots, self.strategy['side'], self.can_socket),
                           'cup': game_logic.CupTask(self.robots, self.strategy['side'], self.can_socket)
                           }
        self.run()

    def run(self):
        self.debugger.start()
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
            print("Robot small")
            self.robots['me'] = PositionMyRobot(self.can_socket, can.MsgTypes.Position_Robot_small.value)
            if self.strategy['robot_big']:
                self.robots['friendly robot'] = PositionOtherRobot(self.can_socket, can.MsgTypes.Position_Robot_big.value)
        elif self.strategy['robot_name'] == 'Roboter-gross':
            print("Robot big")
            self.robots['me'] = PositionMyRobot(self.can_socket, can.MsgTypes.Position_Robot_big.value)
            if self.strategy['robot_small']:
                self.robots['friendly robot'] = PositionOtherRobot(self.can_socket, can.MsgTypes.Position_Robot_small.value)
        else:
            raise Exception("Wrong Robot name")
        if self.strategy['enemy_small']:
            self.robots['enemy1'] = PositionOtherRobot(self.can_socket, can.MsgTypes.Position_Enemy_small.value)
        if self.strategy['robot_big']:
            self.robots['enemy2'] = PositionOtherRobot(self.can_socket, can.MsgTypes.Position_Enemy_big.value)
        self.route_finder.add_my_robot(self.robots['me'])
        for name, robot in self.robots.items():
            if robot is not None and name != 'me':
                self.route_finder.add_robot(robot)
        self.wait_for_game_start()  # start of the game (key removed, emergency stop not pressed)
        self.countdown.start()
        self.can_socket.create_interrupt(can.MsgTypes.Peripherie_inputs.value, self.periphery_input)
        self.countdown.set_interrupt(self.game_end, 'game_end', 2)
        #self.enemy_simulation.start()
        if False:
            arrived = self.can_socket.send_path([], (1000, 1000), 180, end_speed=70, blocking=True)
            print(arrived)
        if False:
            self.strategy_start()
        if True:
            while self.reset is False:
                points = [(900, 1600), (2100, 900), (900, 900), (2100, 1600)]
                for point in points:
                    for i in range(1):
                        #path, path_len = self.route_finder.calculate_path(point)
                        arrived = self.can_socket.send_path([], point, 180, end_speed=30, blocking=True)
        time.sleep(9999999)

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
            if self.strategy['strategy'] == 0:
                self.game_tasks['stand'].do_task(5)
                self.game_tasks['stand'].do_task(6)
                self.game_tasks['stand'].do_task(1)
                #self.game_tasks['cup'].do_task(0)
                #self.game_tasks['stand'].do_task(1)
                self.can_socket.send_path([], (1500, 1000), 180, True)
                can_msg = {
                    'type': can.MsgTypes.Stands_Command.value,
                    'command': self.game_tasks['stand'].command['open case'],
                }
                self.can_socket.send(can_msg)

            elif self.strategy['strategy'] == 1:
                raise Exception('Strategy not programmed')
            elif self.strategy['strategy'] == 2:
                raise Exception('Strategy not programmed')

        if self.strategy['robot_name'] == 'Roboter-klein':
            if self.strategy['strategy'] == 0:
                self.game_tasks['stair'].do_task()
            elif self.strategy['strategy'] == 1:
                raise Exception('Strategy not programmed')
            elif self.strategy['strategy'] == 2:
                raise Exception('Strategy not programmed')
if __name__ == "__main__":
    while True:
        main_program = Main()
        print("Robot Resets")