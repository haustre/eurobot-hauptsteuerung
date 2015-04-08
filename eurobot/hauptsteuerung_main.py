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
        self.speed = 25
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
            'robot_name': hostname, 'side': 'left', 'strategy': 0
        }
        self.robots = {'me': None, 'friendly robot': None, 'enemy1': None, 'enemy2': None}

        self.game_tasks = {'clapper': game_logic.ClapperTask(self.robots, self.strategy['side'], self.can_socket),
                           'stair': game_logic.StairTask(self.robots, self.strategy['side'], self.can_socket),
                           'stand': game_logic.StandsTask(self.robots, self.strategy['side'], self.can_socket)
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
        self.can_socket.send(can_msg)  #TODO: uncomment !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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
        can_msg = {  # TODO: create function for each starting point
            'type': can.MsgTypes.Goto_Position.value,
            'x_position': 600,
            'y_position': 1000,
            'angle': 0,
            'speed': 25,
            'path_length': 0,
        }
        #self.can_socket.send(can_msg)
        #self.wait_for_arrival()
        if False:
            (x, y), angle = self.game_tasks['clapper'].goto_task(1)
            path, path_len = self.route_finder.calculate_path((x, y))
            self.send_path(path, (x, y), angle)
            time.sleep(15)
            self.game_tasks['clapper'].do_task(1)
        if False:
            can_msg = {  # TODO: create function for each starting point
                'type': can.MsgTypes.Goto_Position.value,
                'x_position': 2045,
                'y_position': 1460,
                'angle': 0,
                'speed': 25,
                'path_length': 0,
            }
            self.can_socket.send(can_msg)
        if True:
            self.strategy_start()
        time.sleep(9999999)
        while self.reset is False:
            points = [(990, 1210), (2000, 1200)]
            for point in points:
                for i in range(10):
                    path, path_len = self.route_finder.calculate_path(point)
                    if path_len < 999999999999:     # TODO: define max
                        self.send_path(path, point, 0)
                    elif False:
                        can_msg = {
                            'type': can.MsgTypes.Emergency_Stop.value,
                            'code': 0
                        }
                        self.can_socket.send(can_msg)
                    time.sleep(0.2)

    def wait_for_game_start(self):
        peripherie_queue = queue.Queue()
        queue_number = self.can_socket.create_queue(can.MsgTypes.Peripherie_inputs.value, peripherie_queue)
        game_started = False
        while game_started is False:
            peripherie_msg = peripherie_queue.get()
            if peripherie_msg['key_inserted'] == 0:
                game_started = True
        self.can_socket.remove_queue(queue_number)

    def wait_for_arrival(self,):    # TODO: add timeout
        can_queue = queue.Queue()
        queue_number = self.can_socket.create_queue(can.MsgTypes.Drive_Status.value, can_queue)
        arrived = False
        while arrived is False:
            can_msg = can_queue.get()
            if can_msg['status'] == 0:
                arrived = True
        self.can_socket.remove_queue(queue_number)

    def periphery_input(self, can_msg):
        if can_msg['emergency_stop'] == 1 and can_msg['key_inserted'] == 0 and False:  # TODO: activate
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
            #self.reset = True  # TODO: activate

    def send_path(self, path, destination, angle, blocking=False):
        can_msg = {  # TODO: add angle, speed
            'type': can.MsgTypes.Goto_Position.value,
            'x_position': int(destination[0]),
            'y_position': int(destination[1]),
            'angle': int((abs(angle) % 36000)*100),
            'speed': self.speed,
            'path_length': len(path),
        }
        self.can_socket.send(can_msg)
        time.sleep(0.002)
        if len(path) > 0:
            for point in path:
                can_msg = {
                    'type': can.MsgTypes.Path.value,
                    'x': point[0],
                    'y': point[1],
                    'speed': self.speed
                }
                self.can_socket.send(can_msg)
        if blocking:   # TODO: add timeout
            self.wait_for_arrival()

    def calculate_stoping_point(self, from_pos, to_pos, distance):
        stoping_point = [0, 0]
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        angle = math.atan(abs(dx/dy))
        x = math.sin(angle) * distance
        y = math.cos(angle) * distance
        if to_pos[0] - from_pos[0] > 0:
            stoping_point[0] = int(to_pos[0] - x)
        else:
            stoping_point[0] = int(to_pos[0] + x)
        if to_pos[1] - from_pos[1] > 0:
            stoping_point[1] = int(to_pos[1] - y)
        else:
            stoping_point[1] = int(to_pos[1] + y)
        return stoping_point, angle / (2 * math.pi) * 360

    def send_task_command(self, msg_id, command, blocking=False):  # TODO: Not tested
        can_msg = {
            'type': msg_id,
            'command': command,
        }
        self.can_socket.send(can_msg)
        if blocking:
            self.wait_for_task(msg_id, 0)

    def wait_for_task(self, msg_id, value):
        can_queue = queue.Queue()
        queue_number = self.can_socket.create_queue(msg_id, can_queue)
        finished = False
        while finished is False:
            can_msg = can_queue.get()
            if can_msg['state'] == value:
                finished = True
        self.can_socket.remove_queue(queue_number)

    def strategy_start(self):
        if self.strategy['strategy'] == 0:
            starting_point = self.robots['me'].get_position()
            position_stand1 = self.game_tasks['stand'].my_game_elements[5]['position']
            position_stand2 = self.game_tasks['stand'].my_game_elements[6]['position']
            can_msg = {
                'type': can.MsgTypes.Stands_Command.value,
                'command': self.game_tasks['stand'].command['ready collect'],
            }
            self.can_socket.send(can_msg)
            point, angle = self.calculate_stoping_point(starting_point, position_stand1, 170)
            self.send_path([], point, angle, True)
            self.wait_for_task(can.MsgTypes.Stands_Status.value, 0)
            point, angle = self.calculate_stoping_point(position_stand1, position_stand2, 170)
            self.send_path([], point, angle, True)
            self.send_path([], (1500, 1000), 18000, True)
            self.wait_for_arrival()
            can_msg = {
                'type': can.MsgTypes.Stands_Command.value,
                'command': self.game_tasks['stand'].command['open case'],
            }
            self.can_socket.send(can_msg)

        elif self.strategy['strategy'] == 1:
            pass
        elif self.strategy['strategy'] == 2:
            pass

if __name__ == "__main__":
    while True:
        main_program = Main()
        print("Robot Resets")