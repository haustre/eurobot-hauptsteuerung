__author__ = 'Würsch Marcel'
__license__ = "GPLv3"

import unittest
from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt
import laptop_main
from eurobot.libraries import can


class MyTestCase(unittest.TestCase):
    def setUp(self):
        can_connection = can.Can('vcan0', can.MsgSender.Debugging)

        # Initialization
        self.app = QApplication([])
        # Main Window creation.
        self.MainWin = laptop_main.CanWindow()
        # EXECUTION
        self.MainWin.show()
        QTest.qWaitForWindowShown(self.MainWin)
        # Don't call exec or your qtest commands won't reach widgets.

    def tearDown(self):
        del self.MainWin

    def test_something(self):
        self.MainWin.edit_host.host_line.clear()
        QTest.keyClicks(self.MainWin.edit_host.host_line, "localhost")
        QTest.mouseClick(self.MainWin.edit_host.host_button, Qt.LeftButton, delay=1)




