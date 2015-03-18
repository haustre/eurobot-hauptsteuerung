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
                print('Wrong Hostname\nSet Hostname to "Roboter-klein" or "Roboter-gross"')
                sys.exit(0)
        self.can_socket = can.Can(can_connection, can.MsgSender.Hauptsteuerung)
        self.countdown = game_logic.Countdown(self.can_socket)
        self.debugger = debug.LaptopCommunication(self.can_socket)
        self.route_finder = route_finding.RouteFinding()
        self.enemy_simulation = debug.EnemySimulation(self.can_socket,  3, 70)
        self.strategy = {
            'enemy count': 2, 'friend count': '1', 'robot name': hostname, 'robot color': 'green', 'strategy': 0
        }
        self.robots = {'my': None, 'friendly robot': None, 'enemy1': None, 'enemy2': None}
        self.run()

    def run(self):
        self.debugger.start()
        # TODO: get information from gui
        self.robots['my'] = RobotPosition(self.can_socket, can.MsgTypes.Position_Robot_1)
        if self.strategy['friend count'] == 1:
            self.robots['friendly robot'] = RobotPosition(self.can_socket, can.MsgTypes.Position_Robot_2)
        if self.strategy['enemy count'] >= 1:
            self.robots['enemy1'] = RobotPosition(self.can_socket, can.MsgTypes.Position_Enemy_1.value)
        if self.strategy['enemy count'] == 2:
            self.robots['enemy2'] = RobotPosition(self.can_socket, can.MsgTypes.Position_Enemy_2.value)
        self.wait_for_game_start()  # start of the game (key removed, emergency stop not pressed)
        self.countdown.start()
        self.enemy_simulation.start()
        while True:
            route = self.route_finder.calculate_path(self.robots['enemy1'].get_position(), self.robots['enemy2'].get_position())
            print(route)
            time.sleep(2)

    def wait_for_game_start(self):
        peripherie_queue = queue.Queue()
        self.can_socket.create_queue(can.MsgTypes.Peripherie_inputs.value, peripherie_queue)    # TODO: delete after start
        game_started = False
        while game_started is False:
            peripherie_msg = peripherie_queue.get()
            if peripherie_msg['emergency_stop'] is False and peripherie_msg['key_is_removed'] is True:
                game_started = True


class RobotPosition():
    def __init__(self, can_socket, msg_type):
        self.position = (0, 0)
        self.angle = 0
        self.can_queue = queue.Queue()
        can_socket.create_queue(msg_type, self.can_queue)
        self.lock = threading.Lock()
        self.listen_can = threading.Thread(target=self.listen_can_loop)
        self.listen_can.setDaemon(1)
        self.listen_can.start()

    def listen_can_loop(self):
        while True:
            can_msg = self.can_queue.get()
            with self.lock:
                self.position = can_msg['x_position'], can_msg['y_position']
                self.angle = can_msg['angle']

    def get_position(self):
        with self.lock:
            return self.position

    def get_angle(self):
        with self.lock:
            return self.angle

if __name__ == "__main__":
    main_program = Main()