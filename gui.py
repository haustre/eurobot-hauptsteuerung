__author__ = 'mw'

import time
import sys

from PyQt4 import QtGui, QtCore
import gui.can
from PyQt4 import QtGui
import datetime


class CanWindow(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.threads = []
        self.connected = False
        self.can_table = gui.can.CanTable()
        self.edit_host = gui.can.EditHost()
        self.send_can = gui.can.SendCan()
        self.init_ui()

    def init_ui(self):
        self.edit_host.host_button.clicked.connect(self.connect_host)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.can_table)
        vbox.addWidget(self.send_can)
        vbox.addWidget(self.edit_host)
        self.setLayout(vbox)

    def connect_host(self):
        if self.connected is False:
            self.connected = True
            self.edit_host.host_button.setEnabled(False)
            host = self.edit_host.host_line.text()
            port = self.edit_host.port_line.text()
            print(host, port)
            thread = gui.can.TcpConnection(host, port)
            self.connect(thread, QtCore.SIGNAL('tcp_data'), self.can_table.add_data)
            self.connect(thread, QtCore.SIGNAL('tcp connection lost'), self.lost_connection)
            self.threads.append(thread)
            thread.start()
        else:
            print("Already connected")

    def lost_connection(self):
        self.connected = False
        self.edit_host.host_button.setEnabled(True)


class CreateGroupBox(QtGui.QGroupBox):
    def __init__(self, widget, text):
        super().__init__()
        box1 = QtGui.QVBoxLayout()
        box1.addWidget(widget)
        groupbox = QtGui.QGroupBox(text)
        groupbox.setLayout(box1)
        box2 = QtGui.QVBoxLayout()
        box2.addWidget(groupbox)
        self.setLayout(box2)


def main(args):
    app = QtGui.QApplication(args)
    can_window = CanWindow()
    can_window.show()
    sys.exit(app.exec_())

main(sys.argv)