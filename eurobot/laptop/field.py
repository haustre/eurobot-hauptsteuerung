"""
This module draws the Position of the Robots on a map.
The image of the map is loaded from Table.png. And the images of the robots are loaded
from Roboter1.png and Roboter2.png. The resolution of the images is not very important, they get automatically scaled.
"""
__author__ = 'Würsch Marcel'
__license__ = "GPLv3"

import os
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from libraries import can


class GameField(QWidget):  # TODO: add roboter2 and enemy2
    """ This QWidget is displayed in the laptop gi and draws the Position of the Robots on a map. """
    def __init__(self):
        super().__init__()
        self.table_pixmap = QPixmap(os.path.join(os.path.dirname(__file__), 'Table.png'))
        self.robot1_pixmap = QPixmap(os.path.join(os.path.dirname(__file__), 'Robot1.png'))
        self.enemy1_pixmap = QPixmap(os.path.join(os.path.dirname(__file__), 'Robot2.png'))
        self.pixmap_ratio = self.table_pixmap.height() / self.table_pixmap.width()
        self.robot1 = {'x_position': 1500, 'y_position': 1000, 'diameter': 300, 'angle': 0, 'pixmap': self.robot1_pixmap}
        self.enemy1 = {'x_position': 1500, 'y_position': 1000, 'diameter': 300, 'angle': 0, 'pixmap': self.enemy1_pixmap}

        policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)

    def heightForWidth(self, width):
        return self.pixmap_ratio * width

    def paintEvent(self, event):
        """ Overrides method: :py:func:`QtGui.paintEvent`

        This method is called every time the map is repainted.
        The map is repainted every time one of the following things happens:

        * the gui is opened
        * the window is resized
        * a robot moved and :py:func:`setpoint` is called

        """
        frame_ratio = self.size().height() / self.size().width()
        if frame_ratio > self.pixmap_ratio:
            widget_width = self.size().width()
            widget_height = widget_width * self.pixmap_ratio
        else:
            widget_height = self.size().height()
            widget_width = widget_height / self.pixmap_ratio
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)  # Doesnt make a big difference
        painter.drawPixmap(0, 0, widget_width, widget_height, self.table_pixmap)
        scale = widget_width / 3000
        self._draw_robot(painter, self.robot1, scale)
        self._draw_robot(painter, self.enemy1, scale)

        painter.end()

    def _draw_robot(self, painter, robot, scale):
        """

        :param painter: painter of the map
        :type painter: QtGui.QPainter
        :param robot: data of the robot
        :type robot: dict
        :param scale: scale of the map
        :type scale: int
        :return: None
        """
        x = robot['x_position'] * scale
        y = robot['y_position'] * scale
        diameter = robot['diameter'] * scale
        raw_pixmap = robot['pixmap']
        scaled_pixmap = raw_pixmap.scaled(diameter, diameter, Qt.KeepAspectRatio)
        rotated_pixmap = scaled_pixmap.transformed(QTransform().rotate(robot['angle']))
        pixmap_width = rotated_pixmap.size().width()
        pixmap_height = rotated_pixmap.size().height()
        painter.drawPixmap(x - pixmap_width/2, y - pixmap_height/2, rotated_pixmap)

    def setpoint(self, msg_frame):
        """ This method checks if a CAN message contains the position of a Robot and actualise the position on the map.

        :param msg_frame: CAN message
        :type msg_frame: dict
        :return: None
        """
        if msg_frame['type'] == can.MsgTypes.Position_Robot_1:
            self.robot1['x_position'] = msg_frame['x_position'] / 10
            self.robot1['y_position'] = msg_frame['y_position'] / 10
            self.robot1['angle'] = msg_frame['angle'] / 100

        elif msg_frame['type'] == can.MsgTypes.Position_Enemy_1:
            self.enemy1['x_position'] = msg_frame['x_position'] / 10
            self.enemy1['y_position'] = msg_frame['y_position'] / 10
            self.enemy1['angle'] = msg_frame['angle'] / 100
        self.update()