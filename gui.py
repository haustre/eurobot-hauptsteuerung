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
        header = ['Time', 'Source', 'Type', 'Value']
        self.can_table = gui.can.Table(header)
        self.edit_host = gui.can.EditHost(self)
        self.init_ui()

    def init_ui(self):
        self.edit_host.host_button.clicked.connect(self.connect_host)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.can_table)
        vbox.addWidget(self.edit_host)
        self.setLayout(vbox)

    def connect_host(self):
        if self.connected is False:
            host = self.edit_host.host_line.text()
            port = self.edit_host.port_line.text()
            print(host, port)
            thread = gui.can.Test(host, port)
            self.connect(thread, QtCore.SIGNAL('testsignal'), self.test)
            self.threads.append(thread)
            thread.start()
        else:
            print("Already connected")

    def test(self, data):
        current_time = datetime.datetime.now().strftime("%M:%S.%f")[0:-3]
        for line in data:
            self.can_table.add_row([current_time, str(line[0]), str(line[1])])


def main(args):
    app = QtGui.QApplication(args)
    can_window = CanWindow()
    can_window.show()
    sys.exit(app.exec_())

main(sys.argv)