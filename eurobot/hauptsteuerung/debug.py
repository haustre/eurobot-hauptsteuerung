"""
This module contains the debugging functions for the Beaglebone .
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import threading
import queue
import time
import datetime
import json
import random
import math
from libraries import can
from libraries.ethernet import Server


class LaptopCommunication():
    def __init__(self, can_socket):
        """
        This class starts a tcp server on the Beaglebone and starts the communication to the computer.

        * All received CAN messages are sent to the Laptop over tcp.
        * All the commands received over tcp are send over CAN.
        * All CAN messages are logged to a logfile (logfile.txt)
        """
        self.can_socket = can_socket
        self.tcp_socket = Server()
        self.game_tasks = {}
        self.can_thread = threading.Thread(target=self.can_loop)
        self.can_thread.setDaemon(1)
        self.game_task_thread = threading.Thread(target=self.game_task_loop)
        self.game_task_thread.setDaemon(1)

    def can_loop(self):
        """
        This is the main debugging thread. """
        logfile = open('logfile.txt', 'a')  # TODO: close File at the end of the program
        while True:
            idle = True
            # send new can messages to laptop
            try:
                tcp_msg = 'Can', self.can_socket.queue_debug.get_nowait()
                self.tcp_socket.write(tcp_msg)
                current_time = datetime.datetime.now().strftime("%M:%S.%f")[0:-3]
                text = "\n" + current_time + ": "
                logfile.write(text)  # TODO:  the write commands are blocking and should be put in a separate thread.
                json.dump(tcp_msg, logfile)
                idle = False
            except queue.Empty:
                pass
            # get messages from laptop
            tcp_data = self.tcp_socket.read_no_block()
            if tcp_data:
                self.can_socket.send(tcp_data)
                idle = False
            if idle is True:
                time.sleep(0.01)  # TODO: remove

    def start_can(self):
        """ starts to send the CAN information over ethernet """
        self.can_thread.start()

    def start_game_tasks(self):
        """ starts to send the game task information over ethernet """
        self.game_task_thread.start()

    def game_task_loop(self):
        """ loop sending the game task information """
        while True:
            for task in self.game_tasks.keys():
                time.sleep(0.1)
                tcp_msg = 'game_task', self.game_tasks[task].get_debug_data()
                self.tcp_socket.write(tcp_msg)

    def add_game_tasks(self, game_tasks):
        self.game_tasks = game_tasks


class EnemySimulation():
    """
    This Class simulates the enemy robots
    The simulation is used to test the pathfinding and the game strategy.
    """
    def __init__(self, can_socket, robot_count, speed):
        self.can_socket = can_socket
        self.simulate_enemy = threading.Thread(target=self.simulate_enemy_loop)
        self.simulate_enemy.setDaemon(1)
        self.robots = []
        for robot in range(robot_count):
            self.robots.append(Position(speed))

    def simulate_enemy_loop(self):
        while True:
            for i, robot in enumerate(self.robots):
                msg_type = can.MsgTypes.Position_Robot_small.value + i
                x, y, angle = robot.get_coordinates()
                can_msg = {
                    'type': msg_type,
                    'position_correct': True,
                    'angle_correct': True,
                    'angle': angle,
                    'y_position': y,
                    'x_position': x
                }
                self.can_socket.send(can_msg)
                for queue in self.can_socket.msg_queues:
                    msg_type, msg_queue = queue
                    if msg_type == can_msg['type']:
                        msg_queue.put_nowait(can_msg)
                for interrupt in self.can_socket.msg_interrupts:
                    msg_type, function = interrupt
                    if msg_type == can_msg['type']:
                        function(can_msg)
            time.sleep(0.1)

    def start(self):
        self.simulate_enemy.start()

    def stop_enemy(self):   # TODO: implement
        pass


class Position():
    """ This class generates the coordinates of a virtual robot. """
    def __init__(self, speed):
        self.speed = speed
        self.x = random.randrange(0, 3000)
        self.y = random.randrange(0, 1500)
        self.angle = random.randrange(0, 36000)

    def get_coordinates(self):
        """

        :return: coordinates of the robot (x, y, angel)
        """
        self.angle += self.speed * 3
        self.x += int(self.speed * math.cos(self.angle / 100 / 360*2*math.pi))
        self.y += int(self.speed * math.sin(self.angle / 100 / 360*2*math.pi))
        if self.x > 3000-self.speed or self.x < self.speed or self.y > 2000-self.speed or self.y < self.speed:
            self.angle += 18000
        if self.angle > 36000:
            self.angle -= 36000
        return self.x, self.y, self.angle