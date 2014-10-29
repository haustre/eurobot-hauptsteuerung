__author__ = 'mw'

from PyQt4 import QtGui


class Table(QtGui.QTableWidget):
    def __init__(self, header):
        super().__init__(5, len(header))
        self.header = header
        self.setHorizontalHeaderLabels(header)
        self.verticalHeader().setVisible(False)
        #self.resizeColumnsToContents()
        #self.resizeRowsToContents()
        self.test()

    def test(self):
        for i in range(100):
            self.setRowCount(self.rowCount() + 1)
            for ii in range(len(self.header)):
                newitem = QtGui.QTableWidgetItem(str(i+0.2*ii))
                self.setItem(i, ii, newitem)
                #time.sleep(0.1)