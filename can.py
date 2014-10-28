__author__ = 'mw'

import socket
import struct
import threading
import time


class Can(object):
    def __init__(self, can_id, can_mask):
        self.can_frame_fmt = "=IB3x8s"
        self.queue_receive = Queue()
        self.queue_send = Queue()
        self.s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        can_filter = struct.pack("=II", can_id, can_mask)
        self.s.setsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_FILTER, can_filter)
        self.s.bind(('vcan0', ))
        self.t_connection = threading.Thread(target=self.connection, args=[self.s])
        self.t_connection.setDaemon(1)
        self.t_connection.start()

    def build_can_frame(self, can_id, data):
        can_dlc = len(data)
        data = data.ljust(8, b'\x00')
        return struct.pack(self.can_frame_fmt, can_id, can_dlc, data)

    def dissect_can_frame(self, frame):
        can_id, can_dlc, data = struct.unpack(self.can_frame_fmt, frame)
        return can_id, data[:can_dlc]

    def write(self, can_id, data):
        pass

    def receive(self):
        return self.queue_receive.read()

    def recv_can(self, s):
        frame, addr = s.recvfrom(16)
        can_id, data = self.dissect_can_frame(frame)
        return data

    def connection(self, s):
         while 1:
            #send
            try:
                data = self.recv_can(s)
            except socket.timeout:
                continue
            except socket.error:
                print("Server shutdown")
                return
            except:  # some error or connection reset by peer
                #clientExit(s, str(peer))
                print("Server Fail1")
                break
            if not len(data): # a disconnect (socket.close() by client)
                #clientExit(s, str(peer))
                print("Server Fail2")
                break
            else:
                self.queue_receive.write(data)




class Queue(object):

    def __init__(self):
        self.msg = []
        self.read_lock = threading.Lock()
        self.pointer = -1
        self.BUFFERSIZE = 20

    def read(self):
        with self.read_lock:
            if self.pointer >= 0:
                self.pointer -= 1
                return self.msg[self.pointer + 1]

    def write(self, data):
        with self.read_lock:
            self.msg.insert(0, data)
            self.pointer += 1
            if self.pointer > self.BUFFERSIZE - 1:
                self.pointer = self.BUFFERSIZE - 1
            if len(self.msg) > self.BUFFERSIZE:
                self.msg.pop()

if __name__ == '__main__':
    #can_id, can_mask = 0x600, 0x600
    can_id, can_mask = 0x001, 0x003
    s_debug = Can(can_id, can_mask)
    while True:
        data = s_debug.receive()
        if data:
            print(data)
        time.sleep(0.01)


