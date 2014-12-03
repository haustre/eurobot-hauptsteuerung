from unittest import TestCase
import struct

from eurobot.libraries import can


__author__ = 'mw'


class TestCanPacker(TestCase):

    def test_encode_booleans(self):
        bool_list = [False, True, False, True]
        correct_result = 5
        self.assertEqual(can.encode_booleans(bool_list), correct_result)

    def test_decode_booleans(self):
        value = 5
        number_of_bools = 4
        correct_result = [False, True, False, True]
        self.assertEqual(can.decode_booleans(value, number_of_bools), correct_result)

    def test_unpack(self):
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
        can_msg = {
            'type': can.MsgTypes.Position_Robot_1,
            'position_correct': True,
            'angle_correct': False,
            'angle': 234,
            'y_position': 1234,
            'x_position': 2345
        }
        result = can.pack(can_msg, can.MsgSender.Debugging)
        priority = 0x3
        sender = 0x7
        msg_type = 0x3
        can_id = (priority << 9) + (msg_type << 3) + sender
        data_correct = (0 << 1) + (1 << 0)
        packer_format = '!BHHH'
        can_msg = struct.pack(packer_format, data_correct, 234, 1234, 2345)
        self.assertEqual(result, (can_id, can_msg))