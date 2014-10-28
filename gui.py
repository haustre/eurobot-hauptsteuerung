__author__ = 'mw'

import time
from ethernet import Client
from PyQt4 import QtGui
import sys
import threading


class Table(QtGui.QTableWidget):
    def __init__(self, header):
        super().__init__(5, len(header))
        self.header = header
        self.setHorizontalHeaderLabels(header)
        self.verticalHeader().setVisible(False)
        #self.resizeColumnsToContents()
        #self.resizeRowsToContents()
        #self.test()

    def test(self):
        for i in range(100):
            self.setRowCount(self.rowCount() + 1)
            for ii in range(len(self.header)):
                newitem = QtGui.QTableWidgetItem(str(i+0.2*ii))
                self.setItem(i, ii, newitem)
                time.sleep(0.1)


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


def test2():
    while 1:
        print("Hallo")
        time.sleep(2)


def main(args):
    app = QtGui.QApplication(args)
    header = ['Time', 'Source', 'Type']
    can_table = Table(header)
    can_table.show()

    t = threading.Thread(target=test2)
    t.setDaemon(1)
    t.start()


    sys.exit(app.exec_())



main(sys.argv)