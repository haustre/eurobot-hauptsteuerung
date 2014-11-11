__author__ = 'mw'

import time
import sys

from PyQt4 import QtGui, QtCore
from gui.qt_table import Table
from ethernet import Client
#import threading
import datetime


class CanWindow(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.threads = []
        self.connected = False
        header = ['Time', 'Source', 'Type', 'Value']
        self.can_table = Table(header)
        self.init_ui()

    def init_ui(self):
        edit_host = EditHost(self)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.can_table)
        vbox.addWidget(edit_host)

        self.setLayout(vbox)

    def connect_host(self, host, port):
        print(host, port)
        #t = threading.Thread(target=self.test, args=[host, port])
        #self.threads.append(t)
        #t.setDaemon(1)
        #t.start()
        thread = test(host, port)
        self.connect(thread, QtCore.SIGNAL('testsignal'), self.test)
        self.threads.append(thread)
        thread.start()

    def test(self, line):
        self.can_table.add_row([str(line[0]), str(line[1])])

class test(QtCore.QThread):
    def __init__(self, host, port):
        QtCore.QThread.__init__(self)
        self.host = host
        self.port = port
        self.connected = False

    def run(self):
        tcp = Client(self.host, int(self.port))
        if tcp.connected is True:
            self.connected = True
            while True:
                data = tcp.read()
                if data:
                    current_time = datetime.datetime.now().strftime("%M:%S.%f")[0:-3]
                    for line in data:
                        #self.parent.can_table.add_row([current_time, str(line[0]), str(line[1])])
                        self.emit(QtCore.SIGNAL('testsignal'), line)
                time.sleep(0.5)
        else:
            return


class EditHost(QtGui.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        host_label = QtGui.QLabel('Host:')
        self.host_line = QtGui.QLineEdit('localhost')
        port_label = QtGui.QLabel('Port:')
        self.port_line = QtGui.QLineEdit('42233')
        host_button = QtGui.QPushButton('Connect')
        host_button.clicked.connect(self.connect_host)

        grid = QtGui.QGridLayout()
        grid.addWidget(host_label, 0, 0)
        grid.addWidget(self.host_line, 0, 1)
        grid.addWidget(port_label, 1, 0)
        grid.addWidget(self.port_line, 1, 1)
        grid.addWidget(host_button, 1, 2)
        self.setLayout(grid)

    def connect_host(self):
        if self.parent.connected is False:
            self.parent.connect_host(self.host_line.text(), self.port_line.text())
        else:
            print("Already connected")


def main(args):
    app = QtGui.QApplication(args)
    can_window = CanWindow()
    can_window.show()
    sys.exit(app.exec_())

main(sys.argv)