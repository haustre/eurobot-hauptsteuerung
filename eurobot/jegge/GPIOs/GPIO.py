"""
******************************************************************************************************
 Project           Eurobot 2015
 Filename          GPIO.py

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
from PyQt4 import QtGui, QtCore
import time
from enum import Enum
import sys



"""
-----------------------------------------------------------------------------------------------------
LedClass():
-----------------------------------------------------------------------------------------------------
This Class will control the LED of the BBB-BFH Cape via Sysfs.
It containts Methods to set and reset the LEDs
-----------------------------------------------------------------------------------------------------
"""
class LedClass():
    def __init__(self, Led):
        self.myLed = Led
        self.SYSFSPATH = '/sys/class/gpio/'
        fileExport = open('%sexport' % (self.SYSFSPATH), 'w')
        fileExport.write(self.myLed)
        fileExport.flush()
        fileExport.close()

        fileSetDir = open('%sgpio%s/direction' % (self.SYSFSPATH, self.myLed), 'w')
        fileSetDir.write('out')
        fileSetDir.flush()
        fileSetDir.close()

    def on(self):
        fileSetValue = open('%sgpio%s/value' % (self.SYSFSPATH, self.myLed), 'w')
        fileSetValue.write('0')
        fileSetValue.flush()
        fileSetValue.close()

    def off(self):
        fileSetValue = open('%sgpio%s/value' % (self.SYSFSPATH, self.myLed), 'w')
        fileSetValue.write('1')
        fileSetValue.flush()
        fileSetValue.close()

    def __del__(self):
        fileUnexport = open('%sunexport' % (self.SYSFSPATH), 'w' )
        fileUnexport.write(self.myLed)
        fileUnexport.flush()
        fileUnexport.close()
"""
-----------------------------------------------------------------------------------------------------
ButtonClass():
-----------------------------------------------------------------------------------------------------
This Class will control the Buttons of the BBB-BFH Cape via Sysfs. It contains the method to read
the Buttons
-----------------------------------------------------------------------------------------------------
"""
class ButtonClass():
    def __init__(self, Button):
        self.myButton = Button
        self.SYSFSPATH = '/sys/class/gpio/'
        fileExport = open( '%sexport' % (self.SYSFSPATH), 'w')
        fileExport.write(self.myButton)
        fileExport.flush()
        fileExport.close()
        fileSetDir = open('%sgpio%s/direction' % (self.SYSFSPATH, self.myButton), 'w')
        fileSetDir.write('in')
        fileSetDir.flush()
        fileSetDir.close()

    def getValue(self):
        fileSetValue = open('%sgpio%s/value' %(self.SYSFSPATH, self.myButton), 'r')
        value = fileSetValue.read()
        fileSetValue.flush()
        fileSetValue.close()
        return value

    def __del__(self):
        fileUnexport = open('%sunexport' % (self.SYSFSPATH) , 'w')
        fileUnexport.write(self.myButton)
        fileUnexport.flush()
        fileUnexport.close()








"""
-----------------------------------------------------------------------------------------------------
PollingButton(QtCore.QThread):
-----------------------------------------------------------------------------------------------------
This Class will poll the Buttons from the Beagel Bone Black. This Class is running as Thread.
In addition it controll the whole Menu.
-----------------------------------------------------------------------------------------------------
"""
class PollingButton(QtCore.QThread):

    def __init__(self,parent):
        QtCore.QThread.__init__(self)

        self.parent = parent
        self.BtnActualy = [0 ,0 ,0 ,0, 0, 0]
        self.BtnOld = [0 ,0 ,0 ,0, 0, 0]
        self.BtnPositiveEdge = [False ,False ,False ,False, False ,False]
        self.StateMenu = 0
        self.StateTeamColor = 0
        self.StateNumberofEnemy = 0
        self.StateStrategy = 0
        self.StateTeamColorChange = False
        self.StateNumberofEnemyChange = False
        self.StateStrategyChange = False
        self.StateMenuChange = False

        # Define Constantes #
        self.MaxMenu = 3
        self.MaxSubMenuTeamColor = 2
        self.MaxSubMenuNumberofEnemy = 2
        self.MaxSubMenuStateStrategy = 3

        # Define Object for Buttons #
        self.Btn_up    = ButtonClass('51')
        self.Btn_down  = ButtonClass('112')
        self.Btn_left  = ButtonClass('48')
        self.Btn_right = ButtonClass('49')
        self.Btn_enter = ButtonClass('7')

    def run(self):

        # Endless Loop #
        while True:

            #########################################
            # Checking for positive Edge of Buttons #
            #########################################
            self.BtnActualy = [self.Btn_up.getValue() , self.Btn_down.getValue(), self.Btn_left.getValue() , self.Btn_right.getValue(), self.Btn_enter.getValue()]

            print(self.Btn_up.getValue())
            print(self.Btn_left.getValue())
            for Counter in range(4):
               if (self.BtnActualy[Counter]== 0) and (self.BtnOld[Counter] == 1):
                   self.BtnPositiveEdge[Counter] = True
                   print("positive Flanke")
               else:
                    self.BtnPositiveEdge[Counter] = False
                    print("nichts Flanke")

            ##########################
            # Checking of Menu State #
            ##########################
            # Check if ButtonEnter or Button  Down is active #
            self.StateMenu = State.Enemy._value_
            if self.BtnPositiveEdge[Button.enter._value_] == 1 or self.BtnPositiveEdge[Button.down._value_]:
                self.StateMenu = self.StateMenu + 1
                print( self.StateMenu)
                self.StateMenuChange = True
            # Check if Button Up is active #

            if self.BtnPositiveEdge[Button.up._value_] == 1:
                self.StateMenu = self.StateMenu - 1
                self.StateMenuChange = True

            # Check for Overflow/ Underflow of State #
            if self.StateMenu == self.MaxMenu:
                self.StateMenu = State.TeamColor._value_
            elif self.StateMenu == -1:
                self.StateMenu = self.MaxMenu-1

            ##############################
            # Checking of Submenu State #
            ##############################
            if self.StateMenu == State.TeamColor._value_:

                # Set Cursor if new change to this Menu #
                # Its necessary to read the Settings, that you can control the Menu with Touchscreen and Buttons #
                if self.StateMenuChange == True:
                    (self.StateTeamColor,Settings2,Settings3) = self.parent.getAllSettings()
                    self.StateTeamColorChange = True
                    self.StateMenuChange = False

                 # check if Button Right/Left is active #
                 # Its necessary to read the Settings, that you can control the Menu with Touchscreen and Buttons #
                if self.BtnPositiveEdge[Button.right._value_] == True:
                    (self.StateTeamColor,Settings2,Settings3) = self.parent.getAllSettings()
                    self.StateTeamColor = self.StateTeamColor + 1
                    self.StateTeamColorChange= True
                elif self.BtnPositiveEdge[Button.left._value_] == True:
                    (self.StateTeamColor,Settings2,Settings3) = self.parent.getAllSettings()
                    self.StateTeamColor = self.StateTeamColor - 1
                    self.StateTeamColorChange = True

                # check for Overflow/Underflow of State #
                if self.StateTeamColor == self.MaxSubMenuTeamColor:
                    self.StateTeamColor = 0
                elif self.StateTeamColor == -1:
                    self.StateTeamColor = self.MaxSubMenuTeamColor - 1

            elif self.StateMenu == State.Enemy._value_:

                # Set Cursor if new change to this Menu #
                # Its necessary to read the Settings, that you can control the Menu with Touchscreen and Buttons #
                if self.StateMenuChange == True:
                    (Settings1,self.StateNumberofEnemy,Settings3) = self.parent.getAllSettings()
                    self.StateNumberofEnemyChange = True
                    self.StateMenuChange = False

                # Check if Button Right/Left is active #
                # Its necessary to read the Settings, that you can control the Menu with Touchscreen and Buttons #
                if self.BtnPositiveEdge[Button.right._value_] == True:
                    (Settings1,self.StateNumberofEnemy,Settings3) = self.parent.getAllSettings()
                    self.StateNumberofEnemy = self.StateNumberofEnemy + 1
                    self.StateNumberofEnemyChange = True
                elif self.BtnPositiveEdge[Button.left._value_] == True:
                    (Settings1,self.StateNumberofEnemy,Settings3) = self.parent.getAllSettings()
                    self.StateNumberofEnemy = self.StateNumberofEnemy - 1
                    self.StateNumberofEnemyChange = True

                 # check for Overflow/Underflow of State #
                if self.StateNumberofEnemy == self.MaxSubMenuNumberofEnemy:
                    self.StateNumberofEnemy = 0
                elif self.StateNumberofEnemy == -1:
                    self.StateNumberofEnemy = self.MaxSubMenuNumberofEnemy - 1

            elif self.StateMenu == State.Strategy._value_:

                # Set Cursor if new change to this Menu #
                # Its necessary to read the Settings, that you can control the Menu with Touchscreen and Buttons #
                if self.StateMenuChange == True:
                    (Settings1,Settings2,self.StateStrategy) = self.parent.getAllSettings()
                    self.StateStrategyChange = True
                    self.StateMenuChange = False

                # Check if Button Right/Left is active #
                # Its necessary to read the Settings, that you can control the Menu with Touchscreen and Buttons #
                if self.BtnPositiveEdge[Button.right._value_] == True:
                    (Settings1,Settings2,self.StateStrategy) = self.parent.getAllSettings()
                    self.StateStrategy = self.StateStrategy + 1
                    self.StateStrategyChange = True
                elif self.BtnPositiveEdge[Button.left._value_] == True:
                    (Settings1,Settings2,self.StateStrategy) = self.parent.getAllSettings()
                    self.StateStrategy = self.StateStrategy - 1
                    self.StateStrategyChange = True

                # check for Overflow/Underflow  of State #
                if self.StateStrategy == self.MaxSubMenuStateStrategy:
                    self.StateStrategy = 0
                elif self.StateStrategy == -1:
                    self.StateStrategy = self.MaxSubMenuStateStrategy - 1

            ###################################
            # Sending Settings to GUI-Thread ##
            ###################################
            if self.StateTeamColor == 0 and self.StateTeamColorChange == True:
                self.emit(QtCore.SIGNAL('Settings_TeamColor'), "Yellow")
                self.StateTeamColorChange = False
            elif self.StateTeamColor  == 1 and self.StateTeamColorChange == True:
                self.emit(QtCore.SIGNAL('Settings_TeamColor'), "Green")
                self.StateTeamColorChange = False

            if self.StateNumberofEnemy == 0 and self.StateNumberofEnemyChange == True:
                self.emit(QtCore.SIGNAL('Settings_NumberofEnemy'), "1")
                self.StateNumberofEnemyChange = False
            elif self.StateNumberofEnemy == 1 and self.StateNumberofEnemyChange == True:
                self.emit(QtCore.SIGNAL('Settings_NumberofEnemy'), "2")
                self.StateNumberofEnemyChange = False

            if self.StateStrategy == 0 and self.StateStrategyChange == True:
                self.emit(QtCore.SIGNAL('Settings_Strategy'), "A")
                self.StateStrategyChange = False
            elif self.StateStrategy == 1 and self.StateStrategyChange == True:
                self.emit(QtCore.SIGNAL('Settings_Strategy'), "B")
                self.StateStrategyChange = False
            elif self.StateStrategy == 2 and self.StateStrategyChange == True:
                self.emit(QtCore.SIGNAL('Settings_Strategy'), "C")
                self.StateStrategyChange = False

              # Update BtnOld Variable #
            for Counter in range(4):
                self.BtnOld[Counter] = self.BtnActualy[Counter]

            # Wait for 20ms #
            time.sleep(0.02)


class Button(Enum):
        up    = 0
        down  = 1
        left  = 2
        right = 3
        enter = 4

class State (Enum):
        TeamColor= 0
        Enemy    = 1
        Strategy = 2

"""
-----------------------------------------------------------------------------------------------------
ChasingLED(QtCore.QThread):
-----------------------------------------------------------------------------------------------------
This Class will chase the LED on the Beagel Bone Black. This Class is a running as Thread.
-----------------------------------------------------------------------------------------------------
"""
class ChasingLED(QtCore.QThread):

    def __init__(self):
        QtCore.QThread.__init__(self)

        # Define Object for LEDs #
        self.Led1 = LedClass('61')
        self.Led2 = LedClass('44')
        self.Led3 = LedClass('68')
        self.Led4 = LedClass('67')
        self.LedArr = [self.Led1, self.Led2, self.Led3, self.Led4]

        # Resete all LEDs #
        self.Led1.off()
        self.Led2.off()
        self.Led3.off()
        self.Led4.off()

    def run(self):
        while True:
            i = 0
            while i<= 3:
                self.Led1.off()
                self.Led2.off()
                self.Led3.off()
                self.Led4.off()
                self.LedArr[i].on()
                i = i + 1
                time.sleep(0.05)
            i = 3
            while i >= 0:
                self.Led1.off()
                self.Led2.off()
                self.Led3.off()
                self.Led4.off()
                self.LedArr[i].on()
                i = i - 1
                time.sleep(0.05)

        def __del__(self):
            # Resete all LEDs #
            self.Led1.off()
            self.Led2.off()
            self.Led3.off()
            self.Led4.off()