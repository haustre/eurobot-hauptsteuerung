"""
This module allows to comfortable send and receive CAN messages over socket-CAN. The received messages are given out
as a dictionary. The same dictionary format is also used to send messages.
All dictionaries contain at least a 'type' key. It shows which CAN id is used. The rest of the keys for the different
message types are specified in the EncodingTypes dictionary in this file.
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import socket
import struct
import threading
import queue
import time
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
        self.queue_debug = queue.Queue()
        self.msg_queues = []
        self.msg_interrupts = []
        self.can_frame_fmt = "=IB3x8s"
        self.socket = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        can_filter, can_mask = 0x600, 0x000
        can_filter = struct.pack("=II", can_filter, can_mask)
        self.socket.setsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_FILTER, can_filter)
        self.socket.bind((interface, ))
        self.t_recv_connection = threading.Thread(target=self._recv_connection)
        self.t_recv_connection.setDaemon(1)
        self.t_recv_connection.start()
        self.t_send_connection = threading.Thread(target=self._send_connection)
        self.t_send_connection.setDaemon(1)
        self.t_send_connection.start()

    def create_queue(self, msg_type, msg_queue):
        self.msg_queues.append((msg_type, msg_queue))
        return len(self.msg_queues)-1

    def remove_queue(self, queue_number):
        self.msg_queues.pop(queue_number)

    def create_interrupt(self, msg_type, function):
        self.msg_interrupts.append((msg_type, function))

    def send(self, msg_frame):
        """ Packs a CAN-dictionary to a CAN-frame encodes it and puts it in the send queue

        :param msg_frame: CAN-dictionary
        :return: None
        """
        can_id, can_msg = _pack(msg_frame, self.sender)
        frame = self._build_can_frame(can_id, can_msg)
        self.queue_send.put_nowait((can_id, can_msg))
        self.queue_debug.put_nowait((can_id, can_msg.decode('latin-1')))

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
            msg_frame = unpack(can_id, can_msg)
            for queue in self.msg_queues:   # TODO: very slow
                msg_type, msg_queue = queue
                if msg_type == msg_frame['type']:
                    msg_queue.put_nowait(msg_frame)
            for interrupt in self.msg_interrupts:
                msg_type, function = interrupt
                if msg_type == msg_frame['type']:
                    function(msg_frame)
            self.queue_debug.put_nowait((can_id, can_msg.decode('latin-1')))     # Todo: Check if full

    def _send_connection(self):
        """ Never ending loop for sending CAN messages. """
        while 1:
            can_id, can_msg = self.queue_send.get()
            frame = self._build_can_frame(can_id, can_msg)
            self.socket.send(frame)

    def send_path(self, path, destination, angle, path_speed=25, end_speed=25, blocking=False):
        can_msg = {
            'type': MsgTypes.Goto_Position.value,
            'x_position': int(destination[0]),
            'y_position': int(destination[1]),
            'angle': int((abs(angle) % 360000)*100),
            'speed': end_speed,
            'path_length': len(path),
        }
        self.send(can_msg)
        time.sleep(0.002)
        if len(path) > 0:
            for point in path:
                can_msg = {
                    'type': MsgTypes.Path.value,
                    'x': point[0],
                    'y': point[1],
                    'speed': path_speed
                }
                self.send(can_msg)
        if blocking:   # TODO: add timeout
            self.wait_for_arrival()

    def wait_for_arrival(self,):    # TODO: add timeout
        can_queue = queue.Queue()
        queue_number = self.create_queue(MsgTypes.Drive_Status.value, can_queue)
        arrived = False
        while arrived is False:
            can_msg = can_queue.get()
            if can_msg['status'] == 0:
                arrived = True
        self.remove_queue(queue_number)


def _pack(msg_frame, sender):
    """ Packs dictionary containing the CAN message to the format of the bus.

    :param msg_frame: contains Data to send
    :type msg_frame: dict
    :param sender: defines sender in CAN Id
    :type sender: libraries.can.MsgSender
    :return: can_id, can_msg
    """
    encoding, dictionary = MsgEncoding[msg_frame['type']]
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
    can_id = (priority << 9) + (msg_frame['type'] << 3) + sender
    return can_id, can_msg


def unpack(can_id, can_msg):
    """ Converts raw Can message to a dictionary

    :param can_id:
    :param can_msg:
    :return: msg_frame
    """
    type_mask = 0b00111111000
    type_nr = (can_id & type_mask) >> 3
    msg_type = MsgTypes(type_nr).value
    sender_mask = 0b00000000111
    sender = MsgSender(can_id & sender_mask).value
    encoding, dictionary = MsgEncoding[MsgTypes(type_nr).value]
    try:
        data = struct.unpack(encoding, can_msg)
    except struct.error:
        raise Exception("CAN message encoding wrong:" + encoding + ": " + str(can_msg))
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
    Position_Robot_small = 3
    Position_Robot_big = 4
    Position_Enemy_small = 5
    Position_Enemy_big = 6
    Close_Range_Dedection = 7
    Goto_Position = 8
    Drive_Status = 9
    Stands_Command = 10
    Stands_Status = 11
    Cup_Command = 12
    Cup_Status = 13
    Clapper_Command = 14
    Clapper_Status = 15
    Popcorn_Command = 16
    Popcorn_Status = 17
    Peripherie_inputs = 18
    Debug_Drive = 19
    Configuration = 20
    Board_Status = 21
    Path = 22
    Carpet_Command = 23
    Carpet_Status = 24
    Climbing_Command = 25
    Climbing_Status = 26


class MsgSender(Enum):
    """ This enum contains the names of all possible id's in the CAN header """
    Hauptsteuerung = 0
    Navigation = 1
    Antrieb = 2
    Peripherie = 3
    Debugging = 7

# List of all CAN message protocols
# Format: 'Encoding type: ( Format, (1 Byte, 2 Byte ....)),
EncodingTypes = {
    'game_end':
        ('!B', ['time_to_game_end']),
    'position':
        ('!BHHH', ('x_position', 'y_position', 'angle', ('position_correct', 'angle_correct'))),
    'close_range_dedection':
        ('!BBHHH', ('distance_front_left', 'distance_front_middle', 'distance_front_right',
                    ('front_left_correct', 'front_middle_correct', 'front_right_correct', ),
                    ('sensor1', 'sensor2', 'sensor3', 'sensor4'))),
    'goto_position':
        ('!BbHHH', ('x_position', 'y_position', 'angle', 'speed', 'path_length')),
    'drive_status':
        ('!BB', (('status'), 'time_to_destination')),
    'task_command':
        ('!B', ['command']),
    'task_status':
        ('!BB', ('state', 'collected_pieces')),
    'peripherie':
        ('!BB', (['emergency_stop', 'key_inserted'])),
    'debug_drive':
        ('!hh', ('speed_left', 'speed_right')),
    'emergency':
        ('!B', ['code']),
    'configuration':
        ('!BB', ('reserve', ('is_robot_small', 'is_robot_big', 'is_enemy_small', 'is_enemy_big',
                  'start_left', 'start_orientation'))),
    'Board_Status':
        ('!BB', (('config_complete'), 'error_code')),
    'Path':
        ('!bHH', ('x', 'y', 'speed'))
}

# the list contains which message type is encoded with which protocol
MsgEncoding = {
    MsgTypes.EmergencyShutdown.value: EncodingTypes['emergency'],
    MsgTypes.Emergency_Stop.value: EncodingTypes['emergency'],
    MsgTypes.Game_End.value: EncodingTypes['game_end'],
    MsgTypes.Position_Robot_small.value: EncodingTypes['position'],
    MsgTypes.Position_Robot_big.value: EncodingTypes['position'],
    MsgTypes.Position_Enemy_small.value: EncodingTypes['position'],
    MsgTypes.Position_Enemy_big.value: EncodingTypes['position'],
    MsgTypes.Close_Range_Dedection.value: EncodingTypes['close_range_dedection'],
    MsgTypes.Goto_Position.value: EncodingTypes['goto_position'],
    MsgTypes.Drive_Status.value: EncodingTypes['drive_status'],
    MsgTypes.Stands_Command.value: EncodingTypes['task_command'],
    MsgTypes.Stands_Status.value: EncodingTypes['task_status'],
    MsgTypes.Cup_Command.value: EncodingTypes['task_command'],
    MsgTypes.Cup_Status.value: EncodingTypes['task_status'],
    MsgTypes.Clapper_Command.value: EncodingTypes['task_command'],
    MsgTypes.Clapper_Status.value: EncodingTypes['task_status'],
    MsgTypes.Popcorn_Command.value: EncodingTypes['task_command'],
    MsgTypes.Popcorn_Status.value: EncodingTypes['task_status'],
    MsgTypes.Peripherie_inputs.value: EncodingTypes['peripherie'],
    MsgTypes.Debug_Drive.value: EncodingTypes['debug_drive'],
    MsgTypes.Configuration.value: EncodingTypes['configuration'],
    MsgTypes.Board_Status.value: EncodingTypes['Board_Status'],
    MsgTypes.Path.value: EncodingTypes['Path']
}

# Colors used in can table (Red, Green, Blue) 0-255
MsgColors = {
    MsgTypes.EmergencyShutdown.value:      (205, 41, 41),
    MsgTypes.Emergency_Stop.value:         (205, 41, 41),
    MsgTypes.Game_End.value:               (41, 205, 41),
    MsgTypes.Position_Robot_small.value:       (41, 205, 180),
    MsgTypes.Position_Robot_big.value:       (31, 154, 135),
    MsgTypes.Position_Enemy_small.value:       (41, 175, 205),
    MsgTypes.Position_Enemy_big.value:       (31, 131, 154),
    MsgTypes.Close_Range_Dedection.value:  (41, 52, 205),
    MsgTypes.Goto_Position.value:          (123, 41, 205),
    MsgTypes.Drive_Status.value:           (205, 41, 183),
    MsgTypes.Debug_Drive.value:            (205, 41, 183),
    MsgTypes.Stands_Command.value:         (205, 41, 183),
    MsgTypes.Stands_Status.value:          (205, 41, 183),
    MsgTypes.Cup_Command.value:            (205, 41, 183),
    MsgTypes.Cup_Status.value:             (205, 41, 183),
    MsgTypes.Clapper_Command.value:        (205, 41, 183),
    MsgTypes.Clapper_Status.value:         (205, 41, 183),
    MsgTypes.Popcorn_Command.value:        (205, 41, 183),
    MsgTypes.Popcorn_Status.value:         (205, 41, 183),
    MsgTypes.Peripherie_inputs.value:      (205, 41, 183),
    MsgTypes.Configuration.value:          (205, 41, 183),
    MsgTypes.Board_Status.value:           (205, 41, 183),
    MsgTypes.Path.value:                   (205, 41, 183),
}