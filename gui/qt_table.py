__author__ = 'mw'

from PyQt4 import QtGui, QtCore


class Table(QtGui.QTableWidget):
    def __init__(self, header):
        super().__init__(1, len(header))
        self.header = header
        self.setHorizontalHeaderLabels(header)
        self.verticalHeader().setVisible(False)
        #self.resizeColumnsToContents()
        #self.resizeRowsToContents()

    def add_row(self, data):
        row_count = self.rowCount()
        row_count += 1
        self.setRowCount(row_count)
        self.hideRow(row_count - 1)
        for i in range(len(data)):
            newitem = QtGui.QTableWidgetItem(data[i])
            self.setItem(row_count - 2, i, newitem)
        slide_bar = self.verticalScrollBar()
        slide_bar.setValue(slide_bar.maximum())
        self.showColumn(row_count)
        print(row_count)