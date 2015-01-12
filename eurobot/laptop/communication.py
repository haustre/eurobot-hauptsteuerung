"""
This module contains all the classes used in the gui to receive CAN messages and display them.
"""
__author__ = 'Würsch Marcel'
__license__ = "GPLv3"

import datetime
import copy
import time
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from libraries import can, ethernet, speak


class Table(QTableWidget):
    """ Draws a table and allows to add new rows and filter them. """
    def __init__(self, header):
        """

        :param header: header displayed on the top of the table
        """
        super().__init__(1, len(header))
        self.setHorizontalHeaderLabels(header)
        self.verticalHeader().setVisible(False)
        #self.resizeColumnsToContents()
        #self.resizeRowsToContents()

    def add_row(self, data, color, autoscroll, visible):
        """ Adds a new row to the table.

        :param data: data for the new row
        :param color: color of the new row
        :type color: can.MsgColors
        :param autoscroll: defines if the table should scroll to the end.
        :type autoscroll: bool
        :param visible: defines if the new row is visible or hidden
        :type visible: bool
        :return:
        """
        max_row_count = 20000
        row_count = self.rowCount()
        self.hideRow(row_count)
        row_count += 1
        self.setRowCount(row_count)
        if visible is False:
            self.hideRow(row_count-2)
        for i in range(len(data)):
            newitem = QTableWidgetItem(data[i])
            if color is not None:
                red, green, blue = color
                newitem.setBackground(QColor(red, green, blue))
            self.setItem(row_count - 2, i, newitem)
        if row_count > max_row_count:
            self.removeRow(0)
        if autoscroll is True:
            slide_bar = self.verticalScrollBar()
            slide_bar.setValue(slide_bar.maximum())
        print(row_count)

    def filter_types(self, types):
        """ Applies a filter to the list and hides unwanted rows

        :param types: defines which types should be visible
        :type types: bool[]
        :return: None
        """
        for row in range(self.rowCount()):
            self.showRow(row)
        for msg_type, visible in enumerate(types):
            if visible is False:
                search_string = can.MsgTypes(msg_type).name
                items_to_hide = self.findItems(search_string, Qt.MatchExactly)
                for item in items_to_hide:
                    self.hideRow(item.row())


class CanTableControl(QWidget):
    """ Controls what will be be shown in the CAN table """
    def __init__(self):
        super().__init__()
        self.autoscroll_box = QCheckBox('Autoscroll')
        self.run_button = QPushButton('run')
        self.run_button.clicked.connect(self.run_button_clicked)
        self.run_button.setCheckable(True)

        grid = QGridLayout()
        grid.setSizeConstraint(QLayout.SetMinAndMaxSize)
        grid.addWidget(self.autoscroll_box, 0, 0)
        grid.addWidget(self.run_button, 0, 1)

        self.type_chechboxes = []
        for i, msg_type in enumerate(can.MsgTypes):
            checkbox = QCheckBox(msg_type.name)
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.change_typ_filter)
            self.type_chechboxes.append(checkbox)
            grid.addWidget(checkbox, i / 2 + 1, i % 2)
        self.setLayout(grid)

    def run_button_clicked(self):
        """ Hides all filter options if new messages are received.

        This is necessary because if the table is filtered while new rows are added the computer will be overloaded.
        """
        if self.run_button.isChecked():
            for checkbox in self.type_chechboxes:
                checkbox.setEnabled(False)
        else:
            for checkbox in self.type_chechboxes:
                checkbox.setEnabled(True)

    def change_typ_filter(self):
        """ Runs a new filter on the table if the filter rules changed """
        checked = []
        for checkbox in self.type_chechboxes:
            checked.append(checkbox.isChecked())
        self.emit(SIGNAL('Filter_changed'), checked)

    def add_data(self, msg_frame):
        """ Puts a new CAN frame in the table

        :param msg_frame: new CAN frame
        :return: None
        """
        msg_frame_copy = copy.copy(msg_frame)
        if self.run_button.isChecked():
            table_sender = str(msg_frame_copy['sender'].name)
            table_type = str(msg_frame_copy['type'].name)
            table_color = can.MsgColors[msg_frame_copy['type'].value]
            visible = self.type_chechboxes[msg_frame_copy['type'].value].isChecked()
            del msg_frame_copy['type']
            del msg_frame_copy['sender']
            table_msg = str(msg_frame_copy)
            current_time = datetime.datetime.now().strftime("%M:%S.%f")[0:-3]
            new_row = [current_time, table_sender, table_type, table_msg]
            autoscroll = self.autoscroll_box.isChecked()
            self.emit(SIGNAL('new_can_Table_Row'), new_row, table_color, autoscroll, visible)


class EditHost(QWidget):
    """ This widget is used to configure the connection to the robot """
    def __init__(self):
        super().__init__()
        host_label = QLabel('Host:')
        self.host_line = QLineEdit('192.168.1.101')
        port_label = QLabel('Port:')
        self.port_line = QLineEdit('42233')
        self.host_button = QPushButton('Connect')

        grid = QGridLayout()
        grid.addWidget(host_label, 0, 0)
        grid.addWidget(self.host_line, 0, 1)
        grid.addWidget(port_label, 1, 0)
        grid.addWidget(self.port_line, 1, 1)
        grid.addWidget(self.host_button, 1, 2)
        self.setLayout(grid)


class TcpConnection(QThread):
    """ This thread receives and sends tcp data """
    def __init__(self, host, port):
        QThread.__init__(self)
        self.host = host
        self.port = port
        self.tcp = ethernet.Client(self.host, int(self.port))

    def run(self):
        """ This endless loop is waiting for new data """
        if self.tcp.connected:
            speak.speak("connect to Robot")
            while True:
                data = self.tcp.read_no_block()
                if self.tcp.connected is False:
                    break
                if data is not None:
                    can_id = data[0]
                    can_msg = data[1].encode('latin-1')
                    msg_frame = can.unpack(can_id, can_msg)
                    self.emit(SIGNAL('tcp_data'), msg_frame)
                else:
                    time.sleep(0.01)
            speak.speak("Connection to Robot lost")
        else:
            speak.speak("connection failed")
        self.emit(SIGNAL('tcp connection lost'))

    def send(self, data):
        self.tcp.write(data)


class SendCan(QWidget):  # Todo: compete class
    """ This widget allows to send CAN messages from the robot """
    def __init__(self):
        super().__init__()
        self.msg_type_label = QLabel('Message Type:')
        self.msg_label = QLabel('Message:')
        self.msg_type_combo = QComboBox()
        msg_types = []
        for msg_type in can.MsgTypes:
            msg_types.append(msg_type.name)
        self.msg_type_combo.addItems(msg_types)
        self.msg_type_combo.currentIndexChanged.connect(self.selection_changed)
        self.send_button = QPushButton('send')

        grid = QGridLayout()
        grid.addWidget(self.msg_type_label, 0, 0)
        grid.addWidget(self.msg_type_combo, 0, 1)
        grid.addWidget(self.send_button, 1, 1)

        grid2 = QGridLayout()
        self.lines = []
        for i in range(8):
            line = QLineEdit("Byte: %s" % i)
            self.lines.append(line)
            grid2.addWidget(line, i / 2 + 1, i % 2)

        vbox = QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addLayout(grid2)

        self.setLayout(vbox)

    def selection_changed(self):
        """ This method updates the text in the fields """
        index = self.msg_type_combo.currentIndex()
        msg_type = can.MsgTypes(index).value
        encoding, dictionary = can.MsgEncoding[msg_type]
        for i, line in enumerate(self.lines):
            if i < len(dictionary):
                line.setText(str(dictionary[i]))
                line.setEnabled(True)
            else:
                line.setEnabled(False)
                line.setText("Byte: %s" % i)
