"""
This module draws the Position of the Robots on a map.
The image of the map is loaded from Table.png. And the images of the robots are loaded
from Roboter1.png and Roboter2.png. The resolution of the images is not very important, they get automatically scaled.
"""
__author__ = 'Wuersch Marcel'
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
        self.path_length = 0
        self.path = []
        self.robot_big = {'x_position': 1500, 'y_position': 1000, 'diameter': 300, 'angle': 0, 'pixmap': self.robot1_pixmap}
        self.robot_small = {'x_position': 1500, 'y_position': 1000, 'diameter': 200, 'angle': 0, 'pixmap': self.robot1_pixmap}
        self.enemy_big = {'x_position': 1500, 'y_position': 1000, 'diameter': 300, 'angle': 0, 'pixmap': self.enemy1_pixmap}
        self.enemy_small = {'x_position': 1500, 'y_position': 1000, 'diameter': 200, 'angle': 0, 'pixmap': self.enemy1_pixmap}

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
        self._draw_robot(painter, self.robot_big, scale)
        self._draw_robot(painter, self.robot_small, scale)
        self._draw_robot(painter, self.enemy_big, scale)
        self._draw_robot(painter, self.enemy_small, scale)
        self._draw_path(painter, scale)

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

    def _draw_path(self, painter, scale):
        """ This method draws the planned route of the Robot

        :param painter: painter used to draw
        :param path: path to draw
        :param scale: scale of the pixels
        :return: None
        """
        if len(self.path) == self.path_length:
            pen = QPen(Qt.darkRed, 8, Qt.SolidLine)
            painter.setPen(pen)
            for point in self.path:
                painter.drawPoint(point[0]*scale, point[1]*scale)

    def setpoint(self, msg_frame):
        """ This method checks if a CAN message contains the position of a Robot and actualise the position on the map.

        :param msg_frame: CAN message
        :type msg_frame: dict
        :return: None
        """
        redraw = False
        if msg_frame['type'] == can.MsgTypes.Position_Robot_small.value:
            self.robot_big['x_position'] = msg_frame['x_position']
            self.robot_big['y_position'] = msg_frame['y_position']
            self.robot_big['angle'] = msg_frame['angle'] / 100
            redraw = True
        elif msg_frame['type'] == can.MsgTypes.Position_Robot_big.value:
            self.robot_small['x_position'] = msg_frame['x_position']
            self.robot_small['y_position'] = msg_frame['y_position']
            self.robot_small['angle'] = msg_frame['angle'] / 100
            redraw = True
        elif msg_frame['type'] == can.MsgTypes.Position_Enemy_small.value:
            self.enemy_big['x_position'] = msg_frame['x_position']
            self.enemy_big['y_position'] = msg_frame['y_position']
            self.enemy_big['angle'] = msg_frame['angle'] / 100
            redraw = True
        elif msg_frame['type'] == can.MsgTypes.Position_Enemy_big.value:
            self.enemy_small['x_position'] = msg_frame['x_position']
            self.enemy_small['y_position'] = msg_frame['y_position']
            self.enemy_small['angle'] = msg_frame['angle'] / 100
            redraw = True
        elif msg_frame['type'] == can.MsgTypes.Goto_Position.value:
            self.path_length = msg_frame['path_length']
            self.path = []
        elif msg_frame['type'] == can.MsgTypes.Path.value:
            self.path.append((msg_frame['point_1_x'], msg_frame['point_1_y']))
            if msg_frame['point_2_x'] != 0:
                self.path.append((msg_frame['point_2_x'], msg_frame['point_2_y']))
            if len(self.path) == self.path_length:
                redraw = True
        elif msg_frame['type'] == can.MsgTypes.Emergency_Stop.value:
            self.path = (0, 0)
        if redraw is True:
            self.update()