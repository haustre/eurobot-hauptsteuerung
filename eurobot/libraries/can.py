__author__ = 'mw'

import socket
import struct
import threading
import queue
from enum import Enum


class Can(object):
    """ This Class allows to send and receive CAN messages

    It starts 2 new threads. One for receiving and one for sending.
    The incoming messages are decoded and put into multiple receive buffers.
    Additionally all raw messages are put in the debug buffer.

    """
    def __init__(self, interface, sender):
        """

        :param interface: hardware interface used to send
        :type interface: str
        :param sender: id of the Sender (defines the sender part in the CAN id)
        :type sender: MsgSender
        """
        self.sender = sender
        self.queue_send = queue.Queue()
        self.queue_debug = queue.Queue()  # Todo: Add all buffers
        self.can_frame_fmt = "=IB3x8s"
        self.socket = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        can_filter, can_mask = 0x600, 0x600
        can_filter = struct.pack("=II", can_filter, can_mask)
        self.socket.setsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_FILTER, can_filter)
        self.socket.bind((interface, ))
        self.t_recv_connection = threading.Thread(target=self._recv_connection)
        self.t_recv_connection.setDaemon(1)
        self.t_recv_connection.start()
        self.t_send_connection = threading.Thread(target=self._send_connection)
        self.t_send_connection.setDaemon(1)
        self.t_send_connection.start()

    def send(self, msg_frame):
        """ Packs a CAN-dictionary to a CAN-frame encodes it and puts it in the send queue

        :param msg_frame: CAN-dictionary
        :return: None
        """
        can_id, can_msg = _pack(msg_frame, self.sender)
        frame = self._build_can_frame(can_id, can_msg)
        self.queue_send.put_nowait((can_id, can_msg))

    def _build_can_frame(self, can_id, data):
        """ builds CAN frame

        :param can_id:
        :param data:
        :return: can_frame
        """
        can_dlc = len(data)
        data = data.ljust(8, b'\x00')
        return struct.pack(self.can_frame_fmt, can_id, can_dlc, data)

    def _dissect_can_frame(self, frame):
        """ reads CAN frame

        :param frame:
        :return: can_id, can_msg
        """
        can_id, can_dlc, data = struct.unpack(self.can_frame_fmt, frame)
        return can_id, data[:can_dlc]

    def _recv_connection(self):
        """ Never ending loop for receiving CAN messages """
        while 1:
            frame, addr = self.socket.recvfrom(16)
            can_id, can_msg = self._dissect_can_frame(frame)

            #msg_frame = can.unpack(can_id, can_msg)
            self.queue_debug.put_nowait((can_id, can_msg.decode('latin-1')))     # Todo: Check if full

    def _send_connection(self):
        """ Never ending loop for sending CAN messages. """
        while 1:
            can_id, can_msg = self.queue_send.get()
            frame = self._build_can_frame(can_id, can_msg)
            self.socket.send(frame)


def _pack(msg_frame, sender):
    """ Packs dictionary containing the CAN message to the format of the bus

    :param msg_frame: contains Data to send
    :type msg_frame: dict
    :param sender: defines sender in CAN Id
    :type sender: libraries.can.MsgSender
    :return: can_id, can_msg
    """
    encoding, dictionary = MsgEncoding[msg_frame['type'].value]
    data = []
    for value in reversed(dictionary):
        if not isinstance(value, str):
            booleans = []
            for bool_value in reversed(value):
                booleans.append(msg_frame[bool_value])
            bool_nr = _encode_booleans(booleans)
            data.append(bool_nr)
        else:
            data.append(msg_frame[value])
    can_msg = struct.pack(encoding, *data)
    priority = 0x3  # Todo: unterscheiden zwischen debug und normal
    sender = sender.value
    can_id = (priority << 9) + (msg_frame['type'].value << 3) + sender
    return can_id, can_msg


def _unpack(can_id, can_msg):
    """ Converts raw Can message to a dictionary

    :param can_id:
    :param can_msg:
    :return: msg_frame
    """
    type_mask = 0b00111111000
    type_nr = (can_id & type_mask) >> 3
    msg_type = MsgTypes(type_nr)
    sender_mask = 0b00000000111
    sender = MsgSender(can_id & sender_mask)
    encoding, dictionary = MsgEncoding[MsgTypes(type_nr).value]
    data = struct.unpack(encoding, can_msg)
    msg_frame = {}
    for i, line in enumerate(reversed(data)):
        if not isinstance(dictionary[i], str):
            booleans = _decode_booleans(line, len(dictionary[i]))
            for ii, bool_value in enumerate(reversed(booleans)):
                msg_frame[dictionary[i][ii]] = bool_value
        else:
            msg_frame[dictionary[i]] = line
    msg_frame['type'] = msg_type
    msg_frame['sender'] = sender
    return msg_frame


def _encode_booleans(bool_lst):
    """ encodes a list of up to 8 booleans to a int

    :param bool_lst: list of booleans
    :rtype: int
    """
    res = 0
    for i, bval in enumerate(reversed(bool_lst)):
        res += int(bval) << i
    return res


def _decode_booleans(value, bits):
    """ decodes an int to a list of booleans

    :param value: value to decode
    :type value: int
    :param bits: number of booleans to decode
    :type bits: int
    :return: list of booleans
    """
    res = []
    for bit in reversed(range(bits)):
        mask = 1 << bit
        res.append((value & mask) == mask)
    return res


class MsgTypes(Enum):
    """ This enum contains the names of all possible CAN message types """
    EmergencyShutdown = 0
    Emergency_Stop = 1
    Game_End = 2
    Position_Robot_1 = 3
    Position_Robot_2 = 4
    Position_Enemy_1 = 5
    Position_Enemy_2 = 6
    Close_Range_Dedection = 7
    Goto_Position = 8
    Drive_Status = 9


class MsgSender(Enum):
    """ This enum contains the names of all possible id's in the CAN header """
    Hauptsteuerung = 0
    Navigation = 1
    Antrieb = 2
    Peripherie = 3
    Debugging = 7

# list of all CAN message protocols
EncodingTypes = {
    'game_end': ('!B', ('time_to_game_end')),
    'position': ('!BHHH', ('x_position', 'y_position', 'angle', ('position_correct', 'angle_correct'))),
    'close_range_dedection': ('!BBHHH', ('distance_front_left', 'distance_front_middle', 'distance_front_right',
                                        ('front_left_correct', 'front_middle_correct', 'front_right_correct', ),
                                        ('sensor1', 'sensor2', 'sensor3', 'sensor4'))),
    'goto_position': ('!HHHH', ('x_position', 'y_position', 'angle', 'speed')),
    'drive_status': ('!BB', (('status'), 'time_to_destination')),
    'task_command': ('!BB', ('task_nr', ('start_task', 'stop_task', 'get_status'))),
    'task_status': ('!BBB', ('task_nr', ('task_ready', 'task_running', 'task_finished'), 'collected_pieces')),
    'peripherie': ('!B', (('emergency_stop', 'key_is_removed')))

}

# the list contains which message type is encoded with which protocol
MsgEncoding = {  # Todo: finish the List
    MsgTypes.Position_Robot_1.value: EncodingTypes['position'],
    MsgTypes.Position_Robot_2.value: EncodingTypes['position'],
    MsgTypes.Position_Enemy_1.value: EncodingTypes['position'],
    MsgTypes.Position_Enemy_2.value: EncodingTypes['position']
}

# Colors used in can table
MsgColors = {
    MsgTypes.EmergencyShutdown.value:      (0, 0, 255),
    MsgTypes.Emergency_Stop.value:         (0, 0, 255),
    MsgTypes.Game_End.value:               (0, 0, 255),
    MsgTypes.Position_Robot_1.value:       (0, 255, 0),
    MsgTypes.Position_Robot_2.value:       (255, 0, 0),
    MsgTypes.Position_Enemy_1.value:       (255, 0, 0),
    MsgTypes.Position_Enemy_2.value:       (255, 0, 0),
    MsgTypes.Close_Range_Dedection.value:  (0, 0, 255),
    MsgTypes.Goto_Position.value:          (0, 0, 255),
    MsgTypes.Drive_Status.value:           (0, 0, 255)
}