__author__ = 'mw'

from PyQt4 import QtGui, QtCore
import time

import ethernet


class Table(QtGui.QTableWidget):
    def __init__(self, header):
        super().__init__(1, len(header))
        self.header = header
        self.setHorizontalHeaderLabels(header)
        self.verticalHeader().setVisible(False)
        self.autoScroll = True
        #self.resizeColumnsToContents()
        #self.resizeRowsToContents()

    def add_row(self, data):
        max_row_count = 10000
        row_count = self.rowCount()
        row_count += 1
        self.hideRow(row_count - 1)
        self.setRowCount(row_count)
        for i in range(len(data)):
            newitem = QtGui.QTableWidgetItem(data[i])
            self.setItem(row_count - 2, i, newitem)
        if row_count > max_row_count:
            self.removeRow(0)
        if self.autoScroll is True:
            slide_bar = self.verticalScrollBar()
            slide_bar.setValue(slide_bar.maximum())
        self.showColumn(row_count)
        print(row_count)


class EditHost(QtGui.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        host_label = QtGui.QLabel('Host:')
        self.host_line = QtGui.QLineEdit('localhost')
        port_label = QtGui.QLabel('Port:')
        self.port_line = QtGui.QLineEdit('42233')
        self.host_button = QtGui.QPushButton('Connect')

        grid = QtGui.QGridLayout()
        grid.addWidget(host_label, 0, 0)
        grid.addWidget(self.host_line, 0, 1)
        grid.addWidget(port_label, 1, 0)
        grid.addWidget(self.port_line, 1, 1)
        grid.addWidget(self.host_button, 1, 2)
        self.setLayout(grid)


class Test(QtCore.QThread):
    def __init__(self, host, port):
        QtCore.QThread.__init__(self)
        self.host = host
        self.port = port
        self.connected = False

    def run(self):
        tcp = ethernet.Client(self.host, int(self.port))
        if tcp.connected is True:
            self.connected = True
            while True:
                data = tcp.read_block()
                self.emit(QtCore.SIGNAL('testsignal'), data)
                if tcp.connected is False:
                    self.connected = False
                    break
        else:
            return