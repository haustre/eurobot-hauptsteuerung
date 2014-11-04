__author__ = 'mw'

from PyQt4 import QtGui


class Table(QtGui.QTableWidget):
    def __init__(self, header):
        super().__init__(0, len(header))
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
                #time.sleep(0.1)

    def add_row(self, data):
        max_row_count = 10
        for i in range(len(data)):
            newitem = QtGui.QTableWidgetItem(data[i])
            row_count = self.rowCount()
            self.setRowCount(row_count + 1)
            self.setItem(row_count, i, newitem)
            print(row_count)
            if row_count > max_row_count:
                self.removeRow(0)
                row_count = self.rowCount()
                self.setRowCount(row_count - 1)