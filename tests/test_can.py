from unittest import TestCase
import can

__author__ = 'mw'


class TestCanPacker(TestCase):

    def test_encode_booleans(self):
        bool_list = [True, False, True, False]
        result = 5
        self.assertEqual(can.CanPacker.encode_booleans(bool_list), result)

    def test_decode_booleans(self):
        value = 5
        number_of_bools = 4
        result = [True, False, True, False]
        self.assertEqual(can.CanPacker.decode_booleans(value, number_of_bools), result)
