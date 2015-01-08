"""
This module contains unittests for CAN packer functions.
"""

__author__ = 'Würsch Marcel'
__license__ = "GPLv3"

from unittest import TestCase
import struct
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