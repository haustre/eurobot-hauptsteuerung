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
        self.route_finder = route_finding.RouteFinding(self.can_socket)
        #self.enemy_simulation = debug.EnemySimulation(self.can_socket,  4, 20)
        self.reset = False
        self.strategy = {
            'robot_small': False, 'robot_big': True, 'enemy_small': False, 'enemy_big': False,
            'robot_name': hostname, 'side': 'left', 'strategy': 2
        }
        self.robots = {'me': None, 'friendly robot': None, 'enemy1': None, 'enemy2': None}
        self.run()

    def run(self):
        self.debugger.start()
        # TODO: get information from gui
        if self.strategy['side'] == 'left':
            side = 1
        else:
            side = 0
        if self.strategy['strategy'] == 0 or self.strategy['strategy'] == 1:
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
        while self.reset is False:
            points = [(990, 1210), (990, 1585)]
            for point in points:
                for i in range(1):
                    path, path_len = self.route_finder.calculate_path(point)
                    if path_len < 999999999999:     # TODO: define max
                        self.send_path(path, point)
                    elif False:
                        can_msg = {
                            'type': can.MsgTypes.Emergency_Stop.value,
                            'code': 0
                        }
                        self.can_socket.send(can_msg)
                    time.sleep(3)

    def wait_for_game_start(self):
        peripherie_queue = queue.Queue()
        queue_number = self.can_socket.create_queue(can.MsgTypes.Peripherie_inputs.value, peripherie_queue)
        game_started = False
        while game_started is False:
            peripherie_msg = peripherie_queue.get()
            if peripherie_msg['emergency_stop'] == 0 and peripherie_msg['key_inserted'] == 0:
                game_started = True
        self.can_socket.remove_queue(queue_number)

    def periphery_input(self, can_msg):
        if can_msg['emergency_stop'] == 1 and can_msg['key_inserted'] == 0:
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

    def send_path(self, path, destination):
        can_msg = {  # TODO: add angle, speed
            'type': can.MsgTypes.Goto_Position.value,
            'x_position': destination[0],
            'y_position': destination[1],
            'angle': 0,
            'speed': 25,
            'path_length': len(path),
        }
        self.can_socket.send(can_msg)
        if len(path) > 0:
            for point in path:
                can_msg = {
                    'type': can.MsgTypes.Path.value,
                    'x': point[0],
                    'y': point[1],
                    'speed': 25
                }
                self.can_socket.send(can_msg)
                time.sleep(0.05)


class RobotPosition():
    def __init__(self, can_socket, msg_type, size):
        self.size = size
        self.position = None
        self.angle = None
        self.lock = threading.Lock()
        resolution = 200
        table_size = 2000
        self.map = np.zeros((resolution*1.5, resolution))
        self.scale = table_size / resolution
        self.last_position_update = 0
        self.last_angle_update = 0
        can_socket.create_interrupt(msg_type, self.can_robot_position)

    def can_robot_position(self, can_msg):
        margin = int(20 * self.scale)
        # TODO: check sender ID (in case drive and navigation both send)
        if can_msg['position_correct']:
            x, y = can_msg['x_position'], can_msg['y_position']
            with self.lock:
                self.position = x, y
                self.map[round(x / self.scale) - margin: round(x / self.scale) + margin,
                         round(y / self.scale) - margin: round(y / self.scale) + margin] += 1
            self.last_position_update = time.time()
        if can_msg['angle_correct']:
            with self.lock:
                self.angle = can_msg['angle']
            self.last_angle_update = time.time()

    def get_position(self):
        with self.lock:
            return self.position

    def get_angle(self):
        with self.lock:
            return self.angle

    def get_map(self):
        with self.lock:
            return self.map


class PositionMyRobot(RobotPosition):
    def __init__(self, can_socket, msg_type, size=20):
        super().__init__(can_socket, msg_type, size)


class PositionOtherRobot(RobotPosition):
    def __init__(self, can_socket, msg_type, size=20):
        super().__init__(can_socket, msg_type, size)
        self.check_thread = threading.Thread(target=self.check_navigation)
        self.check_thread.setDaemon(1)
        self.check_thread.start()

    def check_navigation(self):
        while True:
            now = time.time()
            if now - self.last_position_update > 0.1:
                self.angle = None
            if now - self.last_angle_update > 0.1:
                self.position = None
            time.sleep(0.03)

if __name__ == "__main__":
    while True:
        main_program = Main()
        print("Robot Resets")