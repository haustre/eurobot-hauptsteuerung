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

    def add_row(self, data):
        row_count = self.rowCount()
        row_count += 1
        self.setRowCount(row_count)
        self.hideRow(row_count)
        for i in range(len(data)):
            newitem = QtGui.QTableWidgetItem(data[i])
            self.setItem(row_count-1, i, newitem)
        self.scrollToItem(newitem, QtGui.QAbstractItemView.PositionAtCenter)
        self.selectRow(row_count-1)
        self.showColumn(row_count)
        #print(row_count)