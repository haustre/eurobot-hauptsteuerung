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
from eurobot.libraries import can
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
        self.debug_loop = threading.Thread(target=self.can_loop)
        self.debug_loop.setDaemon(1)

    def can_loop(self):
        """
        This is the main debugging thread.
        """
        logfile = open('logfile.txt', 'a')  # TODO: close File at the end of the program
        while True:
            idle = True
            # send new can messages to laptop
            try:
                can_msg = self.can_socket.queue_debug.get_nowait()
                self.tcp_socket.write(can_msg)
                current_time = datetime.datetime.now().strftime("%M:%S.%f")[0:-3]
                text = "\n" + current_time + ": "
                logfile.write(text)  # TODO:  the write commands are blocking and should be put in a separate thread.
                json.dump(can_msg, logfile)
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

    def start(self):
        self.debug_loop.start()


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
                msg_type = can.MsgTypes.Position_Robot_2.value + i
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
                #for queue in self.can_socket.msg_queues:
                #    msg_type, msg_queue = queue
                #    if msg_type == can_msg['type']:
                #        msg_queue.put_nowait(can_msg)
            time.sleep(0.1)

    def start(self):
        self.simulate_enemy.start()

    def stop_enemy(self):   # TODO: implement
        pass


class Position():
    """
    This class generates the coordinates of a virtual robot.
    """
    def __init__(self, speed):
        self.speed = speed
        self.x = random.randrange(0, 30000)
        self.y = random.randrange(0, 15000)
        self.angle = random.randrange(0, 36000)

    def get_coordinates(self):
        self.x += self.speed
        if self.x > 30000:
            self.x = 0
        self.y += self.speed
        if self.y > 15000:
            self.y = 0
        self.angle += self.speed
        if self.angle > 36000:
            self.angle = 0
        return self.x, self.y, self.angle