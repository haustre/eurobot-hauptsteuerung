__author__ = 'mw'

import threading
import queue
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
        while True:  # Todo: log Data to memory
            # send new can messages to laptop
            try:
                can_msg = self.can_socket.queue_debug.get_nowait()
                self.tcp_socket.write(can_msg)
            except queue.Empty:
                pass
            # get messages from laptop
            tcp_data = self.tcp_socket.read_no_block()
            if tcp_data is not None:
                self.can_socket.send(tcp_data)