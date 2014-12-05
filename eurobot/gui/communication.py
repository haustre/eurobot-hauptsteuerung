from eurobot.libraries import can, ethernet, speak

__author__ = 'mw'

from PyQt4 import QtGui, QtCore

import datetime
import copy


class Table(QtGui.QTableWidget):
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
            newitem = QtGui.QTableWidgetItem(data[i])
            if color is not None:
                red, green, blue = color
                newitem.setBackground(QtGui.QColor(red, green, blue))
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
                items_to_hide = self.findItems(search_string, QtCore.Qt.MatchExactly)
                for item in items_to_hide:
                    self.hideRow(item.row())


class CanTableControl(QtGui.QWidget):
    """ Controls what will be be shown in the CAN table """
    def __init__(self):
        super().__init__()
        self.autoscroll_box = QtGui.QCheckBox('Autoscroll')
        self.run_button = QtGui.QPushButton('run')
        self.run_button.clicked.connect(self.run_button_clicked)
        self.run_button.setCheckable(True)

        grid = QtGui.QGridLayout()
        grid.setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize)
        grid.addWidget(self.autoscroll_box, 0, 0)
        grid.addWidget(self.run_button, 0, 1)

        self.type_chechboxes = []
        for i, msg_type in enumerate(can.MsgTypes):
            checkbox = QtGui.QCheckBox(msg_type.name)
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
        self.emit(QtCore.SIGNAL('Filter_changed'), checked)

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
            self.emit(QtCore.SIGNAL('new_can_Table_Row'), new_row, table_color, autoscroll, visible)


class EditHost(QtGui.QWidget):
    """ This widget is used to configure the connection to the robot """
    def __init__(self):
        super().__init__()
        host_label = QtGui.QLabel('Host:')
        self.host_line = QtGui.QLineEdit('localhost')
        port_label = QtGui.QLabel('Port:')
        self.port_line = QtGui.QLineEdit('42233')
        self.host_button = QtGui.QPushButton('Connect')

        grid = QtGui.QGridLayout()
        grid.addWidget(host_label, 0, 0)
        grid.addWidget(self.host_line, 0, 1)
        grid.addWidget(port_label, 1, 0)
        grid.addWidget(self.port_line, 1, 1)
        grid.addWidget(self.host_button, 1, 2)
        self.setLayout(grid)


class TcpConnection(QtCore.QThread):
    """ This thread receives and sends tcp data """
    def __init__(self, host, port):
        QtCore.QThread.__init__(self)
        self.host = host
        self.port = port

    def run(self):
        """ This endless loop is waiting for new data """
        tcp = ethernet.Client(self.host, int(self.port))
        while True:
            data = tcp.read_block()
            if tcp.connected is False:
                break
            can_id = data[0]
            can_msg = data[1].encode('latin-1')
            msg_frame = can._unpack(can_id, can_msg)
            self.emit(QtCore.SIGNAL('tcp_data'), msg_frame)
        speak.speak("Connection to Robot lost")
        self.emit(QtCore.SIGNAL('tcp connection lost'))


class SendCan(QtGui.QWidget):
    """ This widget allows to send CAN messages from the robot """
    def __init__(self):
        super().__init__()
        self.msg_type_label = QtGui.QLabel('Message Type:')
        self.msg_label = QtGui.QLabel('Message:')
        self.msg_type_combo = QtGui.QComboBox()
        msg_types = []
        for msg_type in can.MsgTypes:
            msg_types.append(msg_type.name)
        self.msg_type_combo.addItems(msg_types)
        self.msg_type_combo.currentIndexChanged.connect(self.selection_changed)
        self.send_button = QtGui.QPushButton('send')

        grid = QtGui.QGridLayout()
        grid.addWidget(self.msg_type_label, 0, 0)
        grid.addWidget(self.msg_type_combo, 0, 1)
        grid.addWidget(self.send_button, 1, 1)

        grid2 = QtGui.QGridLayout()
        self.lines = []
        for i in range(8):
            line = QtGui.QLineEdit("Byte: %s" % i)
            self.lines.append(line)
            grid2.addWidget(line, i / 2 + 1, i % 2)

        vbox = QtGui.QVBoxLayout()
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
