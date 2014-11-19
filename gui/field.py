__author__ = 'mw'

from PyQt4 import QtGui, QtCore
import sys


class GameField(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.pixmap = QtGui.QPixmap("./gui/Table.png")
        self.ratio = self.pixmap.height() / self.pixmap.width()

    def paintEvent(self, event):
        #widget_height = self.size().height()
        widget_width = self.size().width()
        widget_height = widget_width * self.ratio
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.drawPixmap(0, 0, widget_width, widget_height, self.pixmap)
        painter.end()

