from eurobot.libraries import speak

__author__ = 'mw'

import sys
from PyQt4 import QtGui, QtCore
import eurobot.gui.field
import eurobot.gui.communication
import eurobot.gui.remote_control


class CanWindow(QtGui.QWidget):
    """ This is the main Widget of the gui """
    def __init__(self):
        super().__init__()
        self.threads = []
        self.connected = False
        header = ['Time', 'Source', 'Type', 'Value']
        self.can_table = eurobot.gui.communication.Table(header)
        self.can_table_control = eurobot.gui.communication.CanTableControl()
        self.edit_host = eurobot.gui.communication.EditHost()
        self.send_can = eurobot.gui.communication.SendCan()
        self.game_field = eurobot.gui.field.GameField()
        self.remote_control = eurobot.gui.remote_control.RemoteControl()
        self.init_ui()

    def init_ui(self):
        """ Initialize different parts of the gui. """
        self.showMaximized()
        self.edit_host.host_button.clicked.connect(self.connect_host)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(CreateGroupBox(self.can_table_control, 'Can Table'))
        vbox.addWidget(CreateGroupBox(self.remote_control, 'Remote Control'))
        vbox.addWidget(CreateGroupBox(self.send_can, 'send Message'))
        vbox.addWidget(CreateGroupBox(self.edit_host, 'connect to Host'))
        vbox.addStretch()
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.game_field, 1)
        hbox.addLayout(vbox)
        root_vbox = QtGui.QVBoxLayout()
        root_vbox.addWidget(self.can_table, 1)
        root_vbox.addLayout(hbox)
        self.setLayout(root_vbox)
        self.connect(self.can_table_control, QtCore.SIGNAL('new_can_Table_Row'), self.can_table.add_row)
        self.connect(self.can_table_control, QtCore.SIGNAL('Filter_changed'), self.can_table.filter_types)

    def connect_host(self):
        """ This method creates a new tcp connection to the robot.

        It is called every time the connect button is pushed.
        """
        if self.connected is False:
            speak.speak("connect to Robot")
            self.connected = True
            self.edit_host.host_button.setEnabled(False)
            host = self.edit_host.host_line.text()
            port = self.edit_host.port_line.text()
            print(host, port)
            thread = eurobot.gui.communication.TcpConnection(host, port)
            self.connect(thread, QtCore.SIGNAL('tcp_data'), self.can_table_control.add_data)
            self.connect(thread, QtCore.SIGNAL('tcp_data'), self.game_field.setpoint)
            self.connect(thread, QtCore.SIGNAL('tcp connection lost'), self.lost_connection)
            self.connect(self.remote_control.control_window, QtCore.SIGNAL('send_tcp'), thread.send)
            self.threads.append(thread)
            thread.start()
        else:
            print("Already connected")

    def lost_connection(self):
        """ This method is called if the tcp connection is lost. """
        self.connected = False
        self.edit_host.host_button.setEnabled(True)


class CreateGroupBox(QtGui.QGroupBox):
    def __init__(self, widget, text):
        """

        :param widget: This widget gets packed in the GroupBox
        :type widget: QtGui.QWidget
        :param text: This is the name of the GroupBox
        :type text: str
        :rtype: QtGui.QGroupBox
        """
        super().__init__()
        box1 = QtGui.QVBoxLayout()
        box1.addWidget(widget)
        groupbox = QtGui.QGroupBox(text)
        groupbox.setLayout(box1)
        box2 = QtGui.QVBoxLayout()
        box2.addWidget(groupbox)
        self.setLayout(box2)


def main(args):
    """ The main function starts the gui """
    app = QtGui.QApplication(args)
    can_window = CanWindow()
    can_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main(sys.argv)