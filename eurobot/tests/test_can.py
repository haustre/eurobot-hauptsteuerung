"""
This module contains unittests for CAN packer functions.
"""

__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import struct
import time
import random
from unittest import TestCase
from eurobot.libraries import can


class TestCanPacker(TestCase):
    """ Unittest for CAN packer """
    def test_encode_booleans(self):
        """
        This function packs 5 booleans to an int and checks if it is correct.
        """
        bool_list = [False, True, False, True]
        correct_result = 5
        self.assertEqual(can._encode_booleans(bool_list), correct_result)

    def test_decode_booleans(self):
        """
        This function unpacks an int to 5 booleans and checks if they are correct.
        """
        value = 5
        number_of_bools = 4
        correct_result = [False, True, False, True]
        self.assertEqual(can._decode_booleans(value, number_of_bools), correct_result)

    def test_unpack(self):
        """
        This functions converts a CAN message to a dictionary  and checks if it is correct.
        """
        priority = 0x3
        sender = 0x0
        msg_type = 0x3
        can_id = (priority << 9) + (msg_type << 3) + sender
        data_correct = (0 << 1) + (1 << 0)
        packer_format = '!BHHH'
        can_msg = struct.pack(packer_format, data_correct, 234, 1234, 2345)
        msg_frame = can.unpack(can_id, can_msg)
        correct_result = (False, True, 234, 1234, 2345, can.MsgTypes.Position_Robot_1, can.MsgSender.Hauptsteuerung)
        result = msg_frame['angle_correct'], msg_frame['position_correct'], msg_frame['angle'],\
            msg_frame['y_position'], msg_frame['x_position'], msg_frame['type'], msg_frame['sender']
        self.assertEqual(correct_result, result)
        pass

    def test_pack(self):
        """
        This function converts a dictionary to a CAN message and checks if it is correct.
        """
        can_msg = {
            'type': can.MsgTypes.Position_Robot_1.value,
            'position_correct': True,
            'angle_correct': False,
            'angle': 234,
            'y_position': 1234,
            'x_position': 2345
        }
        result = can._pack(can_msg, can.MsgSender.Debugging)
        priority = 0x3
        sender = 0x7
        msg_type = 0x3
        can_id = (priority << 9) + (msg_type << 3) + sender
        data_correct = (0 << 1) + (1 << 0)
        packer_format = '!BHHH'
        can_msg = struct.pack(packer_format, data_correct, 234, 1234, 2345)
        self.assertEqual(result, (can_id, can_msg))


class TestCanCommunication(TestCase):
    """ Unittest for The CAN communication with the Discovery Board
    All tests will fail if the Discovery Board is not connected to the computer
    """

    def setUp(self):
        self.can_connection = can.Can('can0', can.MsgSender.Debugging)

    def position_robot_1(self):
        for i in range(10):
            msg_send = {
                'type': can.MsgTypes.Position_Robot_1.value,
                'position_correct': random.choice((True, False)),
                'angle_correct': random.choice((True, False)),
                'angle': random.randrange(0, 36000),
                'y_position': random.randrange(0, 20000),
                'x_position': random.randrange(0, 30000)
            }
            msg_recv = self.compare_send_recv(msg_send)
            self.assertEqual(msg_recv, msg_send)

    def compare_send_recv(self, msg_send):
        self.can_connection.queue_send.put(msg_send)
        time.sleep(0.005)
        msg_rcv = self.can_connection.queue_debug.get_nowait()
        return msg_rcv

    def tearDown(self):
        pass