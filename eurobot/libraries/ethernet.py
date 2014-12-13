__author__ = 'mw'

import socket
import threading
import json
import queue


class _TcpConnection(object):
    """ parent class for Server and Client """
    def __init__(self):
        self.queue_size = 1000
        self.queue_receive = queue.Queue(self.queue_size)
        self.queues_send = []
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @staticmethod
    def _recv_json(s):
        """ receives a json message from the tcp socket

        :param s: tcp socket for receiving
        :return: None
        """
        data = ''
        size = s.recv(8).decode('UTF-8')
        size = int(size[2:7])
        while len(data) < size:
            datatmp = s.recv(size-len(data)).decode('UTF-8')
            data += datatmp
            if datatmp == '':
                raise RuntimeError("socket connection broken")
        return json.loads(data)

    @staticmethod
    def _send_json(s, data):
        """ sends a json message over the tcp socket

        :param s: tcp socket for sending
        :param data: data to send
        :return: None
        """
        json_data = json.dumps(data)
        data_len = "L=%05ds" % len(json_data)
        data_send = bytes(data_len + json_data, 'UTF-8')
        sent = 0
        while sent < len(data_send):
            sent += s.send(data_send[sent:])

    def _connection(self, s):
        """ creates an endless loop for sending and receiving tcp data

        This method is called every time a new computer connects.

        :param s: tcp socket for the connection
        :return: None
        """
        s.settimeout(0.01)
        queue_send = queue.Queue(self.queue_size)
        connection_nr = len(self.queues_send)
        self.queues_send.append(queue_send)

        while 1:
            queue_send = self.queues_send[connection_nr]
            send = []
            while 1:
                try:
                    line = queue_send.get_nowait()
                    send.append(line)
                except queue.Empty:
                    break
            if send:
                self._send_json(s, send)
            try:
                data = self._recv_json(s)
            except socket.timeout:
                continue
            except socket.error:
                print("Server shutdown")
                break
            except:  # some error or connection reset by peer
                print("Server Fail1")
                break
            if not len(data):  # a disconnect (socket.close() by client)
                print("Server Fail2")
                break
            else:
                for line in data:
                    self.queue_receive.put_nowait(line)
        s.close()
        self.queues_send.pop(connection_nr)

    def read_no_block(self):
        """ This method is used to read one json message

        This method does returns None if no data is available.

        :return: json message or None
        """
        try:
            line = self.queue_receive.get_nowait()
        except queue.Empty:
            return None
        return line

    def read_block(self):
        """ This method is used to read one json message

        This method does wait until new data is available

        :return: json message
        """
        return self.queue_receive.get()

    def write(self, data):
        """ This method writes to the send buffer

        :param data: data to send
        :return: None
        """
        for send_queue in self.queues_send:
            try:
                send_queue.put_nowait(data)
            except queue.Full:
                print("Tcp send Queue full!!")


class Server(_TcpConnection):
    """ Tcp server opens a Port for incoming connections."""
    def __init__(self):
        super().__init__()
        host = ''
        port = 42233  # Port opened for incoming connections
        print(host, port)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((host, port))
        self.s.listen(3)
        # creates new thread that waits for incoming new connections
        self.t_connection = threading.Thread(target=self.wait_connections, args=[self.s])
        self.t_connection.setDaemon(1)
        self.t_connection.start()

    def _connection(self, s):
        """ Overrides method: :py:func:`libraries.ethernet._TcpConnection._connection`

        :param s: tcp socket for the connection
        :return: None
        """
        peer = s.getpeername()
        print("Got connection from ", peer)
        super()._connection(s)

    def wait_connections(self, s):
        """ Endless loop waiting for new connections.

        :param s: tcp socket for the connection
        :return: None
        """
        clients = []
        while 1:
            print("Waiting for Connections")
            try:
                clientsock, clientaddr = s.accept()
            except KeyboardInterrupt:
                s.close()
                for sock in clients:
                    sock.close()
                break
            clients.append(clientsock)
            t = threading.Thread(target=self._connection, args=[clientsock])
            t.setDaemon(1)
            t.start()


class Client(_TcpConnection):
    """ Tcp client connects to the server on the given hostname and port """
    def __init__(self, host, port):
        """ Creates new thread for each new connection.

        :param host: Host name of the server you want to connect to.
        :type host: str
        :param port: Port number of the server you want to connect to.
        :type: int
        """
        super().__init__()
        self.connected = False
        try:
            self.s.connect((host, port))
            self.connected = True
        except socket.gaierror:
            print("Name or service not known")
        else:
            t = threading.Thread(target=self._connection, args=[self.s])
            t.setDaemon(1)
            t.start()

    def _connection(self, s):
        """ Overrides method: :py:func:`libraries.ethernet._TcpConnection._connection`

        :param s: tcp socket for the connection
        :return: None
        """
        super()._connection(s)
        self.connected = False
        self.queue_receive.put_nowait("Connection lost")