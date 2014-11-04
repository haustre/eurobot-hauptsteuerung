__author__ = 'mw'

import socket
import threading
import json
import time
import queue


class TcpConnection(object):
    def __init__(self):
        self.queue_receive = queue.Queue(100)
        self.queue_send = queue.Queue(100)
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
        while 1:
            try:
                send = self.queue_send.get_nowait()
            except queue.Empty:
                pass
            else:
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
                self.queue_receive.put_nowait(data)     # Todo:überprüffen ob voll

        s.close()

    def read(self):
        try:
            data = self.queue_receive.get_nowait()
        except queue.Empty:
            pass
        else:
            return data

    def write(self, data):
        self.queue_send.put_nowait(data)
        # Todo:überprüffen ob voll


class Server(TcpConnection):

    def __init__(self):
        super().__init__()
        host = 'localhost'  #Test
        #host = socket.gethostbyname(socket.gethostname())
        print(host)
        port = 42233        #Test
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
        self.s.connect((host, port))
        t = threading.Thread(target=super().connection, args=[self.s])
        t.setDaemon(1)
        t.start()


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
