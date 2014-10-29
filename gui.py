__author__ = 'mw'

import time
import sys

from PyQt4 import QtGui

from gui.qt_table import Table
from ethernet import Client


def test():
    host = 'localhost'  #Test
    port = 42233        #Test
    data = {'message':'hello world!', 'test': 123.4}
    tcp = Client(host, port)
    #tcp.write(data)
    while 1:
        data = tcp.read()
        if data:
            print(data)
            pass
        time.sleep(0.1)


class CanWindow(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.threads = []
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
        self.can_table.add_row([host, port])



class EditHost(QtGui.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        host_label = QtGui.QLabel('Host:')
        self.host_line = QtGui.QLineEdit('192.168.1.X')
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
        '''
        Todo:
        Input überprüfen
        '''
        self.parent.connect_host(self.host_line.text(), self.port_line.text())



def main(args):
    app = QtGui.QApplication(args)
    can_window = CanWindow()
    can_window.show()
    sys.exit(app.exec_())

main(sys.argv)