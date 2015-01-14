"""
This module contains the remote control window.
It sends motor speed commands to the robot.
The robot is controlled using a slider for speed and the W/A/S/D keys for the direction.
"""
__author__ = 'Würsch Marcel'
__license__ = "GPLv3"

import threading
import time
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from libraries import can


class RemoteControlWindow(QDialog):
    """ This QDialog is used as a separate Window it shows the remote control"""
    def __init__(self, parent=None):
        """
        :param parent: parent widget
        """
        super(RemoteControlWindow, self).__init__(parent)
        self.speed = 0
        self.speed_motor_left = 0
        self.speed_motor_right = 0
        self.drive_button = QPushButton('Drive')
        self.close_button = QPushButton('Close')
        self.speed_label = QLabel('Speed: 0 mm/s')
        self.speed_slider = QSlider(Qt.Horizontal, self, )
        self.timer = QTimer()
        self.timer.timeout.connect(self.control_loop)
        self.timer.start(90)

        self.init_ui()

    def init_ui(self):
        """ Initialises the GUI elements.
        """
        self.setWindowTitle('Remote Control')
        text = "Please drive carefully!!\n" \
            " (W) forward\n" \
            " (S) backwards\n" \
            " (A) left\n" \
            " (D) right\n" \
            "press and hold Drive"
        text_label = QLabel(text)
        self.close_button.clicked.connect(self.close)
        self.speed_slider.valueChanged[int].connect(self.slider_change)
        vbox1 = QVBoxLayout()
        vbox1.addWidget(text_label)
        vbox1.addWidget(self.speed_slider)
        vbox1.addWidget(self.speed_label)
        vbox1.addWidget(self.drive_button)
        vbox1.addWidget(self.close_button)
        self.setLayout(vbox1)

    def slider_change(self, slider_value):
        """ Is called when the speed slider is changed.

        :param slider_value: position of the slider
        """
        slider_value = (slider_value + 1) / 100 * 1000
        self.speed = slider_value
        self.speed_label.setText("Speed: %d mm/s" % self.speed)

    def control_loop(self):
        """ Is called every 90 ms and sends the motor speed to the robot

        If the button is released it sends a speed of 0.
        """
        if self.drive_button.isDown() is False:
            self.speed_motor_left = 0
            self.speed_motor_right = 0
        else:
            print("Motor 1: %d, Motor 2: %d" % (self.speed_motor_left, self.speed_motor_right))
            can_msg = {
                'type': can.MsgTypes.Debug_Drive.value,
                'speed_left': int(self.speed_motor_left),
                'speed_right': int(self.speed_motor_right)
            }
            self.emit(SIGNAL('send_can_over_tcp'), can_msg)

    def keyPressEvent(self, event):
        """ Is called at every key press. It sets the motor speed according to the direction. """
        if type(event) == QKeyEvent and event.isAutoRepeat() is False:
            if event.key() == Qt.Key_W:
                self.speed_motor_left = -self.speed
                self.speed_motor_right = self.speed
            if event.key() == Qt.Key_S:
                self.speed_motor_left = self.speed
                self.speed_motor_right = -self.speed
            if event.key() == Qt.Key_A:
                self.speed_motor_left = self.speed
                self.speed_motor_right = self.speed
            if event.key() == Qt.Key_D:
                self.speed_motor_left = -self.speed
                self.speed_motor_right = -self.speed

    def keyReleaseEvent(self, event):
        """ Is called if a key is released. It sets the speed to 0. """
        if event.isAutoRepeat() is False:
            self.speed_motor_left = 0
            self.speed_motor_right = 0