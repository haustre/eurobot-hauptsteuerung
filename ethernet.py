__author__ = 'mw'

import socket
import threading
import json
import time
import queue


class TcpConnection(object):
    def __init__(self):
        self.queue_size = 1000
        self.queue_receive = queue.Queue(self.queue_size)
        #self.queue_send = Queue()
        self.queues_send = []
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def recv_json(self, s):
        data = ''
        size = s.recv(8).decode('UTF-8')
        size = int(size[2:7])
        while len(data) < size:
            dataTmp = s.recv(size-len(data)).decode('UTF-8')
            data += dataTmp
            if dataTmp == '':
                raise RuntimeError("socket connection broken")
        return json.loads(data)

    def send_json(self, s, data):
        json_data = json.dumps(data)
        data_len = "L=%05ds" % len(json_data)
        data_send = bytes(data_len + json_data, 'UTF-8')
        sent = 0
        while sent < len(data_send):
            sent += s.send(data_send[sent:])

    def connection(self, s):
        #pointer_nr = self.queue_send.add_pointer()
        queue_send = queue.Queue(self.queue_size)
        connection_nr = len(self.queues_send)
        self.queues_send.append(queue_send)

        while 1:
            queue_send = self.queues_send[connection_nr]
            try:
                send = queue_send.get_nowait()
            except queue.Empty:
                send = None
            if send:
                self.send_json(s, send)
            try:
                data = self.recv_json(s)
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
                #self.queue_receive.write_all(data)
                for line in data:
                    self.queue_receive.put_nowait(line)

        s.close()

    def read(self):
        data = []
        while 1:
            try:
                line = self.queue_receive.get_nowait()
            except queue.Empty:
                break
            data.append(line)
        return data

    def write(self, data):
        for queue in self.queues_send:
            queue.put_nowait(data)


class Server(TcpConnection):

    def __init__(self):
        super().__init__()
        host = ''
        port = 42233        #Test
        print(host, port)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((host, port))
        self.s.listen(3)
        self.t_connection = threading.Thread(target=self.wait_connections, args=[self.s])
        self.t_connection.setDaemon(1)
        self.t_connection.start()

    def connection(self, s):
        peer = s.getpeername()
        print("Got connection from ", peer)
        super().connection(s)

    def wait_connections(self, s):
        clients = []
        while 1:
            print("Waiting for Connections")
            try:
                clientsock, clientaddr = s.accept()
                clientsock.settimeout(0.1)
            except KeyboardInterrupt:
                s.close()
                for sock in clients:
                    sock.close()
                break
            clients.append(clientsock)
            t = threading.Thread(target=self.connection, args=[clientsock])
            t.setDaemon(1)
            t.start()


class Client(TcpConnection):

    def __init__(self, host, port):
        super().__init__()
        self.connected = False
        try:
            self.s.connect((host, port))
            self.connected = True
        except socket.gaierror:
            print("Name or service not known")
        else:
            t = threading.Thread(target=super().connection, args=[self.s])
            t.setDaemon(1)
            t.start()


class Queue(object):

    def __init__(self):
        self.msg = []
        self.read_lock = threading.Lock()
        self.pointer = -1
        self.tcp_pointer = []

    def add_pointer(self):
        pointer = -1
        with self.read_lock:
            self.tcp_pointer.append(pointer)
            pointer_nr = len(self.tcp_pointer) - 1
            return pointer_nr

    def read(self, pointer_nr=None):
        with self.read_lock:
            if pointer_nr is not None:
                pointer = self.tcp_pointer[pointer_nr]
                if pointer >= 0:
                    self.tcp_pointer[pointer_nr] = -1
                    return self.msg[0: pointer+1]
                else:
                    return None
            else:
                pointer = self.pointer
                if pointer >= 0:
                    self.pointer = -1
                    return self.msg[0: pointer+1]
                    #return self.msg[pointer::-1]

    def write(self, data):
        #print("msg: " + str(self.msg))
        buffersize = 1000
        with self.read_lock:
            self.msg.insert(0, data)
            print(self.msg)
            if len(self.tcp_pointer) > 0:
                for i in range(len(self.tcp_pointer)):
                    self.tcp_pointer[i] += 1
                    if self.tcp_pointer[i] > buffersize - 1:
                        self.tcp_pointer[i] = buffersize - 1
            else:
                self.pointer += 1
                if self.pointer > buffersize - 1:
                    self.pointer = buffersize - 1
            if len(self.msg) > buffersize:
                self.msg.pop()

    def write_all(self, data):
        for line in data:
            self.write(line)

if __name__ == '__main__':
    tcp = Server()
    count = 0
    while 1:
        data = tcp.read()
        if data:
            print(data)
            pass
        tcp.write("Test:" + str(count))
        count += 1
        time.sleep(1)
