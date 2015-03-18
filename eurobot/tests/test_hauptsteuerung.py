"""
This module contains unittests.
"""

__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import time
from unittest import TestCase
from hauptsteuerung import game_logic


class TestHauptsteuerung(TestCase):
    """ Unittest for Hauptsteuerung """
    def test_countdown(self):
        """ starts the countdown and checks if the time_left value is correct and the interrupt is called"""
        countdown = game_logic.Countdown(None)
        self.assertEqual(countdown.time_left(), False)
        countdown.start()
        test_object1 = CountdownTestClass(countdown)
        time.sleep(1.9)
        # Check values before 2 second have passed
        self.assertEqual((countdown.time_left(), test_object1.interrupt_called), (90 - 2, False))
        time.sleep(1.2)
        # Check values after 2 second have passed
        self.assertEqual((countdown.time_left(), test_object1.interrupt_called), (90 - 4, True))


class CountdownTestClass():
    def __init__(self, countdown):
        self.interrupt_called = False
        countdown.set_interrupt(self, '88_seconds_left', 88)

    def interrupt(self, interrupt_name):
        if interrupt_name == '88_seconds_left':
            self.interrupt_called = True
