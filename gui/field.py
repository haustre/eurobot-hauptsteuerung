__author__ = 'mw'

from PyQt4 import QtGui, QtCore
import can
import math


class GameField(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.table_pixmap = QtGui.QPixmap("./gui/Table.png")
        self.robot1_pixmap = QtGui.QPixmap("./gui/Robot1.png")
        self.robot2_pixmap = QtGui.QPixmap("./gui/Robot2.png")
        self.pixmap_ratio = self.table_pixmap.height() / self.table_pixmap.width()
        self.robot1 = (1500, 1000, 300, 0)
        self.enemy2 = (1500, 1000, 300)

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
        painter.setRenderHint(QtGui.QPainter.Antialiasing)  # Todo: check if necessary
        painter.drawPixmap(0, 0, widget_width, widget_height, self.table_pixmap)
        scale = widget_width / 3000

        x, y, diameter, _ = [x * scale for x in self.robot1]
        angle = self.robot1[3]
        #pixmap = self.robot1_pixmap.transformed(QtGui.QTransform().rotate(angle))
        #painter.drawPixmap(x, y, diameter, diameter, pixmap)
        pixmap = self.robot1_pixmap.scaled(diameter, diameter, QtCore.Qt.KeepAspectRatio)
        pixmap = pixmap.transformed(QtGui.QTransform().rotate(angle))
        pixmap_width = pixmap.size().width()
        pixmap_height = pixmap.size().height()
        painter.drawPixmap(x - pixmap_width/2, y - pixmap_height/2, pixmap)

        x, y, diameter = [x * scale for x in self.enemy2]
        painter.drawPixmap(x, y, diameter, diameter, self.robot2_pixmap)

        painter.end()

    def setpoint(self, msg_frame):
        if msg_frame['type'] == can.MsgTypes.Position_Robot_1:
            self.robot1 = (msg_frame['x_position'] / 10, msg_frame['y_position'] / 10, 300, msg_frame['angle'])
            self.update()
        elif msg_frame['type'] == can.MsgTypes.Position_Enemy_1:
            self.enemy2 = (msg_frame['x_position'] / 10, msg_frame['y_position'] / 10, 300)
            self.update()