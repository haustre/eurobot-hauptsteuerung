__author__ = 'mw'

import socket
import struct
import threading
import time
import queue


class Can(object):
    def __init__(self, interface):
        self.can_frame_fmt = "=IB3x8s"
        self.s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        #can_filter = struct.pack("=II", can_id, can_mask)
        self.s.setsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_FILTER)
        self.s.bind((interface, ))
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
                self.queue_receive.put_nowait(data)     # Todo:überprüffen ob voll


class CanRecv(Can):
    def __init__(self):
        self.queue_receive = queue.Queue()
        super().__init__()

    def connection(self, s):
        while 1:
                data = self.recv_can(s)
                self.queue_receive.put_nowait(data)     # Todo:überprüffen ob voll


class CanSend(Can):
    def __init__(self):
        self.queue_send = queue.Queue()
        super().__init__()

    def connection(self, s):
        while 1:
            send_can(self.queue_send)



class CanPacker(object):
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


