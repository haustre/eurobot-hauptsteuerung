__author__ = 'mw'

from PyQt4 import QtGui, QtCore
import threading, time


class RemoteControl(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.controll_active = False
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
        if self.t_control_loop.is_alive() is False:
            self.t_control_loop.start()
        if self.controll_active is False:
            self.activate_button.setText("STOP")
            self.controll_active = True
        else:
            self.activate_button.setText("Activate Remote Control")
            self.controll_active = False

    def control_loop(self):
        count = 0
        while 1:
            if self.controll_active:
                print(count)
                count += 1
            time.sleep(0.2)
