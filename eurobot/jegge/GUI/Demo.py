"""
-----------------------------------------------------------------------------------------------------
ChasingLED(QtCore.QThread):
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
            print(self.parent.getAllSettings())
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
