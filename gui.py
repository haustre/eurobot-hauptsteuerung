__author__ = 'mw'

import time
from ethernet import Client
from PyQt4 import QtGui
import sys

class Table(QtGui.QTableWidget):
    def __init__(self, header):
        super().__init__(1, len(header))
        self.setHorizontalHeaderLabels(header)
        self.verticalHeader().setVisible(False)
        #self.resizeColumnsToContents()
        #self.resizeRowsToContents()


def main(args):
    app = QtGui.QApplication(args)
    header = ['Time', 'Source', 'Type']
    can_table = Table(header)
    can_table.show()
    sys.exit(app.exec_())

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

main(sys.argv)