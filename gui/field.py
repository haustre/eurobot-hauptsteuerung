__author__ = 'mw'

from PyQt4 import QtGui, QtCore
import can
import math


class GameField(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.pixmap = QtGui.QPixmap("./gui/Table.png")
        self.pixmap_ratio = self.pixmap.height() / self.pixmap.width()
        self.robot1 = (1500, 1000, 50, 0)
        self.enemy2 = (1500, 1000, 50)

    def paintEvent(self, event):
        frame_ratio = self.size().height() / self.size().width()
        if frame_ratio > self.pixmap_ratio:
            widget_width = self.size().width()
            widget_height = widget_width * self.pixmap_ratio
        else:
            widget_height = self.size().height()
            widget_width = widget_height / self.pixmap_ratio
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.drawPixmap(0, 0, widget_width, widget_height, self.pixmap)
        scale = widget_width / 3000

        x, y, diameter, _ = [x * scale for x in self.robot1]
        angle = self.robot1[3]
        pen = QtGui.QPen(QtCore.Qt.red, 3, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        painter.drawEllipse(x - diameter / 2, y - diameter / 2, diameter, diameter)
        painter.drawLine(x, y, x + math.sin(angle)*30, y + math.cos(angle)*30)

        x, y, diameter = [x * scale for x in self.enemy2]
        pen = QtGui.QPen(QtCore.Qt.green, 3, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        painter.drawEllipse(x, y, diameter, diameter)

        painter.end()

    def setpoint(self, msg_frame):
        if msg_frame['type'] == can.MsgTypes.Position_Robot_1:
            self.robot1 = (msg_frame['x_position'] / 10, msg_frame['y_position'] / 10, 50, msg_frame['angle'] / 100)
            self.update()
        elif msg_frame['type'] == can.MsgTypes.Position_Enemy_1:
            self.enemy2 = (msg_frame['x_position'] / 10, msg_frame['y_position'] / 10, 50)
            self.update()