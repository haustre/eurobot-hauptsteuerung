__author__ = 'Würsch Marcel'
__license__ = "GPLv3"

import unittest
import sys
from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt
import laptop_main

import time

class MyTestCase(unittest.TestCase):
    def setUp(self):
        app = QApplication(['/home/mw/PycharmProjects/Eurobot/eurobot/laptop_main.py'])
        self.can_window = laptop_main.CanWindow()
        self.can_window.show()
        sys.exit(app.exec_())

    def tearDown(self):
        del self.can_window

    def test_something(self):
        ok_widget = self.can_window.edit_host.host_button(self.can_window.edit_host)
        #okWidget = self.form.ui.buttonBox.button(self.form.ui.buttonBox.Ok)
        QTest.mouseClick(ok_widget, Qt.LeftButton)




