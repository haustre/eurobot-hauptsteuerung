__author__ = 'mw'

import time
import sys

from PyQt4 import QtGui

from qt_table import Table
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
        self.init_ui()



    def init_ui(self):
        header = ['Time', 'Source', 'Type']
        can_table = Table(header)

        edit_host = EditHost()
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(can_table)
        vbox.addWidget(edit_host)
        vbox.addStretch(1)

        self.setLayout(vbox)

    def change_host(self):
        print("Test2")


class EditHost(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        host_label = QtGui.QLabel('Host:')
        host_line = QtGui.QLineEdit('192.168.1.X')
        port_label = QtGui.QLabel('Port:')
        port_line = QtGui.QLineEdit('4223')

        host_button = QtGui.QPushButton('Change')
        host_button.clicked.connect(self.change_host)

        host_box = QtGui.QHBoxLayout()
        host_box.addWidget(host_label)
        host_box.addWidget(host_line)
        port_box = QtGui.QHBoxLayout()
        port_box.addWidget(port_label)
        port_box.addWidget(port_line)
        port_box.addWidget(host_button)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(host_box)
        vbox.addLayout(port_box)
        vbox.addStretch(1)
        self.setLayout(vbox)
        #self.show()

    def change_host(self):
        print("Test")
        #super().change_host()



def main(args):
    app = QtGui.QApplication(args)
    can_window = CanWindow()
    can_window.show()
    sys.exit(app.exec_())

main(sys.argv)