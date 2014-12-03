from eurobot.libraries import can

__author__ = 'mw'

from PyQt4 import QtGui, QtCore


class GameField(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.table_pixmap = QtGui.QPixmap("./gui/Table.png")
        self.robot1_pixmap = QtGui.QPixmap("./gui/Robot1.png")
        self.enemy1_pixmap = QtGui.QPixmap("./gui/Robot2.png")
        self.pixmap_ratio = self.table_pixmap.height() / self.table_pixmap.width()
        self.robot1 = {'x_position': 1500, 'y_position': 1000, 'diameter': 300, 'angle': 0, 'pixmap': self.robot1_pixmap}
        self.enemy1 = {'x_position': 1500, 'y_position': 1000, 'diameter': 300, 'angle': 0, 'pixmap': self.enemy1_pixmap}

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
        self.draw_robot(painter, self.robot1, scale)
        self.draw_robot(painter, self.enemy1, scale)

        painter.end()

    def draw_robot(self, painter, robot, scale):
        x = robot['x_position'] * scale
        y = robot['y_position'] * scale
        diameter = robot['diameter'] * scale
        raw_pixmap = robot['pixmap']
        scaled_pixmap = raw_pixmap.scaled(diameter, diameter, QtCore.Qt.KeepAspectRatio)
        rotated_pixmap = scaled_pixmap.transformed(QtGui.QTransform().rotate(robot['angle']))
        pixmap_width = rotated_pixmap.size().width()
        pixmap_height = rotated_pixmap.size().height()
        painter.drawPixmap(x - pixmap_width/2, y - pixmap_height/2, rotated_pixmap)

    def setpoint(self, msg_frame):
        if msg_frame['type'] == can.MsgTypes.Position_Robot_1:
            self.robot1['x_position'] = msg_frame['x_position'] / 10
            self.robot1['y_position'] = msg_frame['y_position'] / 10
            self.robot1['angle'] = msg_frame['angle'] / 100

        elif msg_frame['type'] == can.MsgTypes.Position_Enemy_1:
            self.enemy1['x_position'] = msg_frame['x_position'] / 10
            self.enemy1['y_position'] = msg_frame['y_position'] / 10
            self.enemy1['angle'] = msg_frame['angle'] / 100
        self.update()