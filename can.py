__author__ = 'mw'

import socket
import struct
import threading
import time
import queue


class Can(object):
    def __init__(self, interface):
        self.queue_send = queue.Queue()
        self.queue_debugg = queue.Queue()
        self.can_frame_fmt = "=IB3x8s"
        self.socket = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        can_id, can_mask = 0x600, 0x600
        can_filter = struct.pack("=II", can_id, can_mask)
        self.socket.setsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_FILTER, can_filter)
        self.socket.bind((interface, ))
        self.t_recv_connection = threading.Thread(target=self.recv_connection)
        self.t_recv_connection.setDaemon(1)
        self.t_recv_connection.start()
        self.t_send_connection = threading.Thread(target=self.send_connection)
        self.t_send_connection.setDaemon(1)
        self.t_send_connection.start()

    def build_can_frame(self, can_id, data):
        can_dlc = len(data)
        data = data.ljust(8, b'\x00')
        return struct.pack(self.can_frame_fmt, can_id, can_dlc, data)

    def dissect_can_frame(self, frame):
        can_id, can_dlc, data = struct.unpack(self.can_frame_fmt, frame)
        return can_id, data[:can_dlc]

    def recv_can(self):
        frame, addr = self.socket.recvfrom(16)
        id, data = self.dissect_can_frame(frame)
        return id, data

    def send_can(self, id, msg):
        frame = self.build_can_frame(id, msg)
        self.socket.send(frame)

    def recv_connection(self):
        while 1:
                data = self.recv_can()
                self.queue_debugg.put_nowait(data)     # Todo:überprüffen ob voll

    def send_connection(self):
        while 1:
            id, msg = self.queue_send.get()
            self.send_can(id, msg)  # blocking

    def send(self, id, msg):
        self.queue_send.put_nowait((id, msg))


class _CanPacker(object):
    def __init__(self):
        types = ["",            # Emergency Shutdown
                 "",            # Emergency Stop
                 "Game_end"]    # Game End
        pass
    
    def pack(self, type, data):
        priority = 0x3  # Debugg
        sender = 0x0  # Kern
        id = priority << 9 + type << 3 + sender
        #packer.unpack(data)



if __name__ == '__main__':
    can_id, can_mask = 0x600, 0x600
    s = Can(can_id, can_mask, 'vcan0')
    while True:
        data = s.receive()
        if data:
            print(data)
        time.sleep(0.01)


