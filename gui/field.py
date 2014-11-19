__author__ = 'mw'

from PyQt4 import QtGui, QtCore
import can
import sys


class GameField(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.packer = can.CanPacker()
        self.pixmap = QtGui.QPixmap("./gui/Table.png")
        self.ratio = self.pixmap.height() / self.pixmap.width()
        self.robot1 = (1500, 1000, 50)

    def paintEvent(self, event):
        #widget_height = self.size().height()
        widget_width = self.size().width()
        widget_height = widget_width * self.ratio
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.drawPixmap(0, 0, widget_width, widget_height, self.pixmap)
        scale = widget_width / 3000
        x, y, diameter = [x * scale for x in self.robot1]
        pen = QtGui.QPen(QtCore.Qt.red, 3, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        painter.drawEllipse(x, y, diameter, diameter)
        painter.end()

    def SetPoint(self, data):
        id = data[0]
        type = (id & 0b00111111000) >> 3
        if can.MsgTypes(type).name == 'Position_Robot_1':
            msg = data[1].encode('latin-1')
            msg_frame = self.packer.unpack(id, msg)
            self.robot1 = (msg_frame['x_position'] / 10, msg_frame['y_position'] / 10, 50)
            self.update()