__author__ = 'mw'

from PyQt4 import QtGui, QtCore
import threading
import time
from eurobot.libraries import speak
from eurobot.libraries import can


class RemoteControl(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.control_active = False
        self.speed_motor_1 = 0
        self.speed_motor_2 = 0
        self.activate_button = QtGui.QPushButton('Activate Remote Control')
        self.control_window = RemoteControlWindow(self)
        self.init_ui()

    def init_ui(self):
        self.activate_button.clicked.connect(self.activate_button_clicked)
        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(self.activate_button)
        self.setLayout(vbox1)

    def activate_button_clicked(self):
        speak.speak("Pleas drive carefully")
        self.control_window.exec_()


class RemoteControlWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(RemoteControlWindow, self).__init__(parent)
        self.speed = 0
        self.speed_motor_left = 0
        self.speed_motor_right = 0
        self.drive_button = QtGui.QPushButton('Drive')
        self.close_button = QtGui.QPushButton('Close')
        self.speed_label = QtGui.QLabel('Speed: 0 mm/s')
        self.speed_slider = QtGui.QSlider(QtCore.Qt.Horizontal, self, )
        self.t_control_loop = threading.Thread(target=self.control_loop)
        self.t_control_loop.setDaemon(1)
        self.t_control_loop.start()

        self.init_ui()

    def init_ui(self):
        text = "Please drive carefully!!\n" \
            " (W) forward\n" \
            " (S) backwards\n" \
            " (A) left\n" \
            " (D) right\n" \
            "press and hold Drive"
        text_label = QtGui.QLabel(text)
        self.close_button.clicked.connect(self.close)
        self.speed_slider.valueChanged[int].connect(self.slider_change)
        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(text_label)
        vbox1.addWidget(self.speed_slider)
        vbox1.addWidget(self.speed_label)
        vbox1.addWidget(self.drive_button)
        vbox1.addWidget(self.close_button)
        self.setLayout(vbox1)

    def slider_change(self, slider_value):
        slider_value = (slider_value + 1) / 100 * 1000
        self.speed = slider_value
        self.speed_label.setText("Speed: %d mm/s" % self.speed)

    def control_loop(self):
        while True:
            if self.drive_button.isDown() is False:
                self.speed_motor_left = 0
                self.speed_motor_right = 0
            else:
                print("Motor 1: %d, Motor 2: %d" % (self.speed_motor_left, self.speed_motor_right))
                can_msg = {
                    'type': can.MsgTypes.Debug_Drive.value,
                    'speed_left': self.speed_motor_left,
                    'speed_right': self.speed_motor_right
                }
                self.emit(QtCore.SIGNAL('send_can_over_tcp'), can_msg)
            time.sleep(0.2)

    def keyPressEvent(self, event):
        if type(event) == QtGui.QKeyEvent and event.isAutoRepeat() is False:
            if event.key() == QtCore.Qt.Key_W:
                self.speed_motor_left = self.speed
                self.speed_motor_right = self.speed
            if event.key() == QtCore.Qt.Key_S:
                self.speed_motor_left = -self.speed
                self.speed_motor_right = -self.speed
            if event.key() == QtCore.Qt.Key_A:
                self.speed_motor_left = -self.speed
                self.speed_motor_right = self.speed
            if event.key() == QtCore.Qt.Key_D:
                self.speed_motor_left = self.speed
                self.speed_motor_right = -self.speed

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat() is False:
            self.speed_motor_left = 0
            self.speed_motor_right = 0