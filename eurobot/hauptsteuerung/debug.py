"""
This module is contains the debugging functions for the Beaglebone that are used to communicate with the computer.
"""
__author__ = 'Würsch Marcel'
__license__ = "GPLv3"

import threading
import queue
import time
import datetime
import json
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
        self.debug_loop = threading.Thread(target=self.run)
        self.debug_loop.setDaemon(1)
        self.debug_loop.start()

    def run(self):
        """
        This is the main debugging thread.
        """
        logfile = open('logfile.txt', 'a')  # TODO: close File at the end of the program
        while True:
            # send new can messages to laptop
            try:
                can_msg = self.can_socket.queue_debug.get_nowait()
                self.tcp_socket.write(can_msg)
                current_time = datetime.datetime.now().strftime("%M:%S.%f")[0:-3]
                text = "\n" + current_time + ": "
                logfile.write(text)  # TODO:  the write commands are blocking and should be put in a separate thread.
                json.dump(can_msg, logfile)
            except queue.Empty:
                pass
            # get messages from laptop
            tcp_data = self.tcp_socket.read_no_block()
            if tcp_data:
                self.can_socket.send(tcp_data)
            time.sleep(0.01)  # TODO: remove