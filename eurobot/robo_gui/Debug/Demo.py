"""
******************************************************************************************************
 Project           Eurobot 2015
 Filename          Demo.py

 Institution:      University of applied Science Bern

 IDE               PyCharm 4.0.3 Build #PY-139.781
 Python            Python 3.4.1

 @author           Yves Jegge und Joel Baertschi
 @date             04.01.2015
 @version          1.0.0

 @copyright        Copyright 2015, Eurobot
 @status           Development

******************************************************************************************************
"""

# Import Librarys #
import random
import time
from PyQt4 import QtCore, QtGui

"""
-----------------------------------------------------------------------------------------------------
PrintOutSettings(QtCore.QThread):
-----------------------------------------------------------------------------------------------------
This Class Print all Actually Settings from the GUI. This Class is a running as Thread
This is only a Debugging Class
-----------------------------------------------------------------------------------------------------
"""
class PrintOutSettings(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)

    def run(self):
        while True:
            time.sleep(4)
"""
-----------------------------------------------------------------------------------------------------
PrintOutSettings(QtCore.QThread):
-----------------------------------------------------------------------------------------------------
This Class Print all Actually Settings from the GUI. This Class is a running as Thread
This is only a Debugging Class
-----------------------------------------------------------------------------------------------------
"""
class PrintOutSettings(QtCore.QThread):

    def __init__(self,parent):
        QtCore.QThread.__init__(self)
        self.parent = parent

    def run(self):
        while True:
            print(self.parent.getAllSettingsString())
            time.sleep(4)
"""
-----------------------------------------------------------------------------------------------------
ChasingLED(QtCore.QThread):
-----------------------------------------------------------------------------------------------------
This Class set new random Coordinate for the Roboter.This Class is a running as Thread
 This is only a Debugging Class
-----------------------------------------------------------------------------------------------------
"""
class SetRandomCoordinate(QtCore.QThread):

    def __init__(self):
        QtCore.QThread.__init__(self)

    def run(self):
        while True:
            X_Coordinate = random.randrange(0, 30000, 1)
            Y_Coordinate = random.randrange(0, 20000, 1)
            Angle= random.randrange(0, 360, 1)

            self.emit(QtCore.SIGNAL('Coordinate'), X_Coordinate, Y_Coordinate, Angle)
            time.sleep(1)

