"""
This is the main file to execute the software of the Beaglebone.
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import sys
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
        self.route_finder = route_finding.RouteFinding()
        self.enemy_simulation = debug.EnemySimulation(self.can_socket,  4, 20)
        self.strategy = {
            'robot_small': True, 'robot_big': True, 'enemy_small': True, 'enemy_big': True,
            'robot_name': hostname, 'side': 'left', 'strategy': 0
        }
        self.robots = {'me': None, 'friendly robot': None, 'enemy1': None, 'enemy2': None}
        self.run()

    def run(self):
        self.debugger.start()
        # TODO: get information from gui
        can_msg = {
            'type': can.MsgTypes.Configuration.value,
            'is_robot_small': self.strategy['robot_small'],
            'is_robot_big': self.strategy['robot_big'],
            'is_enemy_small': self.strategy['enemy_small'],
            'is_enemy_big': self.strategy['enemy_big'],
            'start_left': self.strategy['side'] is 'left',
            'reserve': 0
        }
        self.can_socket.send(can_msg)
        if self.strategy['robot_name'] == 'Roboter-klein':
            print("Robot small")
            self.robots['me'] = RobotPosition(self.can_socket, can.MsgTypes.Position_Robot_small.value)
            if self.strategy['robot_big']:
                self.robots['friendly robot'] = RobotPosition(self.can_socket, can.MsgTypes.Position_Robot_big.value)
        elif self.strategy['robot_name'] == 'Roboter-gross':
            print("Robot big")
            self.robots['me'] = RobotPosition(self.can_socket, can.MsgTypes.Position_Robot_big.value)
            if self.strategy['robot_small']:
                self.robots['friendly robot'] = RobotPosition(self.can_socket, can.MsgTypes.Position_Robot_small.value)
        else:
            print("Wrong Robot name")
        if self.strategy['enemy_small']:
            self.robots['enemy1'] = RobotPosition(self.can_socket, can.MsgTypes.Position_Enemy_small.value)
        if self.strategy['robot_big']:
            self.robots['enemy2'] = RobotPosition(self.can_socket, can.MsgTypes.Position_Enemy_big.value)
        self.route_finder.add_my_robot(self.robots['me'])
        for name, robot in self.robots.items():
            if robot is not None and name != 'me':
                self.route_finder.add_robot(robot)
        self.wait_for_game_start()  # start of the game (key removed, emergency stop not pressed)
        self.countdown.start()
        self.countdown.set_interrupt(self.game_end, 'game_end', 2)
        #self.enemy_simulation.start()
        while True:
            points = [(1000, 800), (2000, 800), (1000, 1700), (2000, 1700)]
            for point in points:
                for i in range(1):
                    path, path_len = self.route_finder.calculate_path(point)
                    if path_len < 200:
                        self.send_path(path, point)
                    else:
                        can_msg = {
                            'type': can.MsgTypes.Emergency_Stop.value,
                            'code': 0
                        }
                        self.can_socket.send(can_msg)
                    time.sleep(3)

    def wait_for_game_start(self):
        peripherie_queue = queue.Queue()
        self.can_socket.create_queue(can.MsgTypes.Peripherie_inputs.value, peripherie_queue)    # TODO: delete after start
        game_started = False
        while game_started is False:
            peripherie_msg = peripherie_queue.get()
            if peripherie_msg['emergency_stop'] is False and peripherie_msg['key_is_removed'] is True:
                game_started = True

    def game_end(self):
        can_msg = {
            'type': can.MsgTypes.EmergencyShutdown.value,
            'code': 0,
        }
        self.can_socket.send(can_msg)

    def send_path(self, path, destination):
        can_msg = {  # TODO: add angle, speed
            'type': can.MsgTypes.Goto_Position.value,
            'x_position': destination[0],
            'y_position': destination[1],
            'angle': 0,
            'speed': 100,
            'path_length': len(path),
        }
        self.can_socket.send(can_msg)
        for i in range(math.floor(len(path) / 2)):
            can_msg = {
                'type': can.MsgTypes.Path.value,
                'point_1_x': path[2*i][0],
                'point_1_y': path[2*i][1],
                'point_2_x': path[2*i+1][0],
                'point_2_y': path[2*i+1][1],
            }
            self.can_socket.send(can_msg)
        if len(path) % 2 != 0:
            can_msg = {
                'type': can.MsgTypes.Path.value,
                'point_1_x': path[len(path)-1][0],
                'point_1_y': path[len(path)-1][1],
                'point_2_x': 0,
                'point_2_y': 0,
            }
            self.can_socket.send(can_msg)


class RobotPosition():
    def __init__(self, can_socket, msg_type, size=20):
        self.size = size
        self.position = (0, 0)
        self.angle = 0
        self.can_queue = queue.Queue()
        self.lock = threading.Lock()
        resolution = 200
        table_size = 2000
        self.map = np.zeros((resolution*1.5, resolution))
        self.scale = table_size / resolution
        can_socket.create_queue(msg_type, self.can_queue)
        self.listen_can = threading.Thread(target=self.listen_can_loop)
        self.listen_can.setDaemon(1)
        self.listen_can.start()

    def listen_can_loop(self):
        margin = int(20 * self.scale)
        while True:
            can_msg = self.can_queue.get()
            x, y = can_msg['x_position'], can_msg['y_position']
            with self.lock:
                self.position = x, y
                self.angle = can_msg['angle']
                self.map[round(x / self.scale) - margin: round(x / self.scale) + margin,
                         round(y / self.scale) - margin: round(y / self.scale) + margin] += 1

    def get_position(self):
        with self.lock:
            return self.position

    def get_angle(self):
        with self.lock:
            return self.angle

    def get_map(self):
        with self.lock:
            return self.map

if __name__ == "__main__":
    main_program = Main()