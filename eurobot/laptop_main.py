"""
This is the main file to execute the GUI software on the computer.
"""
__author__ = 'Würsch Marcel'
__license__ = "GPLv3"

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import laptop.field
import laptop.communication
from laptop.remote_control import RemoteControlWindow
from libraries import speak


class CanWindow(QWidget):
    """ This is the main Widget of the gui """
    def __init__(self):
        super().__init__()
        self.threads = []
        self.connected = False
        header = ['Time', 'Source', 'Type', 'Value']
        self.can_table = laptop.communication.Table(header)
        self.can_table_control = laptop.communication.CanTableControl()
        self.edit_host = laptop.communication.EditHost()
        self.remote_control_button = QPushButton('Activate Remote Control')
        self.send_can = laptop.communication.SendCan()
        self.game_field = laptop.field.GameField()
        self.remote_control_window = RemoteControlWindow(self)
        self.init_ui()

    def init_ui(self):
        """ Initialize different parts of the gui. """
        self.setWindowTitle('Eurobot Robot Control')
        self.showMaximized()
        self.edit_host.host_button.clicked.connect(self.connect_host)
        self.remote_control_button.clicked.connect(self.activate_remote_control)
        self.remote_control_button.setEnabled(False)
        vbox = QVBoxLayout()
        vbox.addWidget(CreateGroupBox(self.can_table_control, 'Can Table'))
        vbox.addWidget(CreateGroupBox(self.remote_control_button, 'Remote Control'))
        #vbox.addWidget(CreateGroupBox(self.send_can, 'send Message'))
        vbox.addWidget(CreateGroupBox(self.edit_host, 'connect to Host'))
        vbox.addStretch()
        hbox = QHBoxLayout()
        hbox.addWidget(self.game_field, 1)
        hbox.addLayout(vbox)
        root_vbox = QVBoxLayout()
        root_vbox.addWidget(self.can_table, 1)
        root_vbox.addLayout(hbox)
        self.setLayout(root_vbox)
        self.connect(self.can_table_control, SIGNAL('new_can_Table_Row'), self.can_table.add_row)
        self.connect(self.can_table_control, SIGNAL('Filter_changed'), self.can_table.filter_types)

    def connect_host(self):
        """ This method creates a new tcp connection to the robot.

        It is called every time the connect button is pushed.
        """
        if self.connected is False:
            self.connected = True
            self.edit_host.host_button.setEnabled(False)
            self.remote_control_button.setEnabled(True)
            host = self.edit_host.host_line.text()
            port = self.edit_host.port_line.text()
            print(host, port)
            thread = laptop.communication.TcpConnection(host, port)
            self.connect(thread, SIGNAL('tcp_data'), self.can_table_control.add_data)
            self.connect(thread, SIGNAL('tcp_data'), self.game_field.setpoint)
            self.connect(thread, SIGNAL('tcp connection lost'), self.lost_connection)
            self.connect(self.remote_control_window, SIGNAL('send_can_over_tcp'), thread.send)
            self.threads.append(thread)
            thread.start()
        else:
            print("Already connected")

    def lost_connection(self):
        """ This method is called if the tcp connection is lost. """
        self.connected = False
        self.edit_host.host_button.setEnabled(True)
        self.remote_control_button.setEnabled(False)

    def activate_remote_control(self):
        """ Opens a new Window for the remote control """
        speak.speak("Please drive carefully")
        self.remote_control_window.exec_()


class CreateGroupBox(QGroupBox):  # TODO: remove second groupbox
    def __init__(self, widget, text):
        """

        :param widget: This widget gets packed in the GroupBox
        :type widget: QtGui.QWidget
        :param text: This is the name of the GroupBox
        :type text: str
        :rtype: QtGui.QGroupBox
        """
        super().__init__()
        box1 = QVBoxLayout()
        box1.addWidget(widget)
        groupbox = QGroupBox(text)
        groupbox.setLayout(box1)
        box2 = QVBoxLayout()
        box2.addWidget(groupbox)
        self.setLayout(box2)


def main(args):
    """ The main function starts the gui """
    app = QApplication(args)
    can_window = CanWindow()
    can_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main(sys.argv)