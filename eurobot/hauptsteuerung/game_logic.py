"""
This module contains classes for the game logic
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import threading
import time
from eurobot.libraries import can


class Countdown():
    def __init__(self, can_socket):
        """
        This class counts down the remaining time till the end of the game
        """
        self.can_socket = can_socket
        self.running = False
        self.start_time = 0
        self.game_time = 90  # Time the end of the game in seconds
        self.timers_to_start = []
        self.timer_loop = threading.Thread(target=self._loop)
        self.timer_loop.setDaemon(1)

    def start(self):
        self.start_time = time.time()
        self.running = True
        for timer in self.timers_to_start:
            threading.Timer(timer).start()
        self.timer_loop.start()

    def time_left(self):
        if self.running:
            time_left = int(self.game_time - (time.time() - self.start_time))
        else:
            time_left = False
        return time_left

    def set_interrupt(self, object_to_call, interrupt_name, time_left):
        if self.running:
            interrupt_time = self.game_time - time_left
            threading.Timer(interrupt_time, object_to_call.interrupt, [interrupt_name]).start()
        else:
            call = object_to_call, interrupt_name, time_left
            self.timers_to_start.append(call)

    def _loop(self):
        time_left = 90
        while time_left >= 0:
            print(time_left)
            can_msg = {
                'type': can.MsgTypes.Game_End.value,
                'time_to_game_end': int(time_left)
            }
            if self.can_socket:
                self.can_socket.send(can_msg)
            time.sleep(0.99)
            time_left = self.start_time + self.game_time - time.time()