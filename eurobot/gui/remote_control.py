__author__ = 'mw'

from PyQt4 import QtGui, QtCore
import threading, time


class RemoteControl(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.control_active = False
        self.speed_motor_1 = 0
        self.speed_motor_2 = 0
        self.activate_button = QtGui.QPushButton('Activate Remote Control')
        self.t_control_loop = threading.Thread(target=self.control_loop)
        self.t_control_loop.setDaemon(1)
        self.init_ui()

    def init_ui(self):
        self.activate_button.clicked.connect(self.activate_button_clicked)
        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(self.activate_button)
        self.setLayout(vbox1)

    def activate_button_clicked(self):
        RemoteControlWindow()
        if self.t_control_loop.is_alive() is False:
            self.t_control_loop.start()
        if self.control_active is False:
            self.activate_button.setText("STOP")
            self.control_active = True
        else:
            self.activate_button.setText("Activate Remote Control")
            self.control_active = False

    def control_loop(self):
        while 1:
            if self.control_active:
                print(self.speed_motor_1)
            time.sleep(0.2)

    def keyPressEvent(self, event):
        if type(event) == QtGui.QKeyEvent and event.key() == QtCore.Qt.Key_A and event.isAutoRepeat() is False:
            self.speed_motor_1 = 10

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat() is False:
            self.speed_motor_1 = 0

    def focusOutEvent(self, event):
        self.speed_motor_1 = 0


class RemoteControlWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(RemoteControlWindow, self).__init__(parent)
        self.t_control_loop = threading.Thread(target=self.control_loop)
        self.t_control_loop.setDaemon(1)
        self.t_control_loop.start()
        self.close_button = QtGui.QPushButton('Close')
        #self.init_ui()

    def init_ui(self):
        text_label = QtGui.QLabel('You now have control')
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.close_button)
        layout.addWidget(text_label)

        self.buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        layout.addWidget(self.buttons)

        #self.setLayout(vbox1)

    def control_loop(self):
        while 1:
            print("hallo")
            time.sleep(0.2)