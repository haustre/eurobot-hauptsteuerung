__author__ = 'mw'

import threading
from eurobot.libraries import can
from eurobot.libraries.ethernet import Server


class LaptopCommunication():
    def __init__(self, can_socket):
        self.can_socket = can_socket
        self.tcp_socket = Server()
        self.debug_loop = threading.Thread(target=self.run)
        self.debug_loop.setDaemon(1)
        self.debug_loop.start()

    def run(self):
        while True:
            can_msg = self.can_socket.queue_debug.get()  # Todo: log Data to memory
            self.tcp_socket.write(can_msg)